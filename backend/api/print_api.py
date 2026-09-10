import base64
import os
import platform
import re
import shutil
import subprocess
import tempfile
import time
from io import BytesIO
from pathlib import Path

from PIL import Image

from conf.config import config
from utilities.log import logger
from utilities.response import res200, res400, res500

# 证件照常用纸张(供下拉框兜底,实际以打印机上报的 MediaSize 为准)
COMMON_MEDIA_SIZES = ["A4", "Letter", "4x6in", "5x7in", "A5"]


def _run_cmd(cmd):
    """执行系统命令,返回 CompletedProcess。"""
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def _cups_available():
    return platform.system() in ("Darwin", "Linux") and shutil.which("lpstat") is not None


def _is_windows():
    return platform.system() == "Windows"


def _windows_printers():
    """用 PowerShell 枚举 Windows 打印机,返回 (names, default_name)。"""
    ps = ["powershell", "-NoProfile", "-NonInteractive", "-Command"]
    names = []
    try:
        proc = subprocess.run(
            ps + ["Get-Printer | ForEach-Object { $_.Name }"],
            capture_output=True, text=True, timeout=30,
        )
        names = [l.strip() for l in (proc.stdout or "").splitlines() if l.strip()]
    except Exception as e:
        logger.error(f"Error listing windows printers: {e}")
    default_name = ""
    try:
        proc = subprocess.run(
            ps + ["(Get-CimInstance Win32_Printer | Where-Object { $_.Default }).Name"],
            capture_output=True, text=True, timeout=30,
        )
        lines = [(l.strip()) for l in (proc.stdout or "").splitlines() if l.strip()]
        if lines:
            default_name = lines[0]
    except Exception as e:
        logger.error(f"Error getting windows default printer: {e}")
    return names, default_name


def _resolve_image_file(playload):
    """把 base64 或本地路径转成待打印的图片文件,返回 (Path, 是否临时文件)。"""
    base64_data = playload.get("base64_data", "")
    image_path = playload.get("image_path", "")
    hex_color = playload.get("hex_color", "transparent")
    if base64_data:
        image_data = base64.b64decode(base64_data.split(",")[1])
        image = Image.open(BytesIO(image_data)).convert("RGBA")
        if hex_color != "transparent":
            from utilities.utils import hex_to_rgb

            bg = Image.new("RGBA", image.size, hex_to_rgb(hex_color) + (255,))
            bg.paste(image, (0, 0), image)
            image = bg
        else:
            # 透明底直接打印多为全白,统一垫白底
            bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
            bg.paste(image, (0, 0), image)
            image = bg
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        image.convert("RGB").save(tmp.name, "PNG")
        tmp.close()
        return Path(tmp.name), True
    if image_path and Path(image_path).exists():
        return Path(image_path), False
    raise FileNotFoundError("No valid base64_data or image_path provided.")


def _print_windows(playload):
    """Windows 打印:图片垫底色后存到 data/print,调系统打印动词(份数/纸张等走打印对话框选)。"""
    startfile = getattr(os, "startfile", None)
    if startfile is None:
        return res400("Windows printing requires os.startfile.")
    try:
        save_dir = Path(config.get("save_dir", "./data")) / "print"
        save_dir.mkdir(parents=True, exist_ok=True)
        image_file, is_temp = _resolve_image_file(playload)
        try:
            dest = save_dir / f"print_{int(time.time() * 1000)}.png"
            if is_temp:
                shutil.move(str(image_file), str(dest))
            else:
                shutil.copy(str(image_file), str(dest))
            startfile(str(dest), "print")
            logger.info(f"Windows print submitted: {dest}")
            return res200(
                data={
                    "job_id": "",
                    "file": str(dest),
                    "tip": "已发送到 Windows 打印,份数/纸张请在系统打印对话框中确认",
                }
            )
        finally:
            if is_temp and image_file.exists():
                try:
                    image_file.unlink()
                except Exception:
                    pass
    except FileNotFoundError as e:
        return res400(str(e))
    except Exception as e:
        logger.error(f"Error in windows print: {e}")
        return res500("Error in windows print")


class PrintAPI:
    name = "print"

    def get_printers(self, playload=None):
        """获取本机打印机列表及默认打印机。"""
        if _is_windows():
            names, default_printer = _windows_printers()
            printers = [
                {"name": n, "status": "", "state": "idle" if n == default_printer else "unknown"}
                for n in names
            ]
            return res200(
                data={
                    "supported": True,
                    "os": "Windows",
                    "printers": printers,
                    "default_printer": default_printer,
                }
            )
        if not _cups_available():
            return res200(
                data={
                    "supported": False,
                    "os": platform.system(),
                    "printers": [],
                    "default_printer": "",
                    "tip": "Printing is supported on Windows/macOS/Linux.",
                }
            )
        try:
            proc = _run_cmd(["lpstat", "-p", "-d"])
            output = (proc.stdout or "") + "\n" + (proc.stderr or "")
            printers = []
            for line in output.splitlines():
                m = re.match(r"^printer\s+(\S+)\s+(.*)$", line.strip())
                if m:
                    name, status = m.group(1), m.group(2)
                    state = "idle"
                    if "disabled" in status:
                        state = "disabled"
                    elif "printing" in status.lower():
                        state = "printing"
                    printers.append({"name": name, "status": status, "state": state})
            default_printer = ""
            m = re.search(r"system default destination:\s*(\S+)", output)
            if m:
                default_printer = m.group(1)
            return res200(
                data={
                    "supported": True,
                    "os": platform.system(),
                    "printers": printers,
                    "default_printer": default_printer,
                }
            )
        except Exception as e:
            logger.error(f"Error in get_printers: {e}")
            return res500("Error in get_printers")

    def get_printer_options(self, playload):
        """获取某台打印机的可选纸张等选项(lpoptions -l)。"""
        printer_name = playload.get("printer_name", "") if isinstance(playload, dict) else ""
        if not _cups_available():
            return res400("Printing is only supported on macOS/Linux with CUPS.")
        if not printer_name:
            return res400("printer_name is required.")
        try:
            proc = _run_cmd(["lpoptions", "-p", printer_name, "-l"])
            if proc.returncode != 0:
                return res400(f"Cannot query printer '{printer_name}': {(proc.stderr or '').strip()}")
            media_sizes = []
            default_media = ""
            for line in (proc.stdout or "").splitlines():
                m = re.match(r"^(\S+?)/[^:]*:\s*(.+)$", line.strip())
                if not m:
                    continue
                key, values = m.group(1), m.group(2)
                if key.lower() in ("mediasize", "pagesize", "media"):
                    for token in values.split():
                        if token.startswith("*"):
                            default_media = token[1:]
                            media_sizes.append(token[1:])
                        else:
                            media_sizes.append(token)
            # 合并常用纸张,去重保序
            merged = list(dict.fromkeys(media_sizes + COMMON_MEDIA_SIZES))
            return res200(data={"media_sizes": merged, "default_media": default_media})
        except Exception as e:
            logger.error(f"Error in get_printer_options: {e}")
            return res500("Error in get_printer_options")

    def print_image(self, playload):
        """打印图片。playload: {base64_data/image_path, printer, copies, media, orientation, fit_to_page, hex_color}。"""
        if _is_windows():
            return _print_windows(playload)
        if not _cups_available():
            return res400("Printing is supported on Windows/macOS/Linux.")
        try:
            printer = (playload.get("printer") or "").strip()
            if not printer:
                printer = (config.get("printer.printer_name", "") or "").strip()
            copies = int(playload.get("copies") or config.get("printer.copies", 1) or 1)
            copies = max(1, min(copies, 99))
            media = (playload.get("media") or config.get("printer.media", "") or "").strip()
            orientation = (playload.get("orientation") or config.get("printer.orientation", "portrait") or "portrait").lower()
            fit_to_page = playload.get("fit_to_page", config.get("printer.fit_to_page", True))
            if fit_to_page in ("false", "False", 0, "0"):
                fit_to_page = False
            else:
                fit_to_page = bool(fit_to_page)

            image_file, is_temp = _resolve_image_file(playload)
            try:
                cmd = ["lp"]
                if printer:
                    cmd += ["-d", printer]
                cmd += ["-n", str(copies)]
                options = []
                if media:
                    options += ["-o", f"media={media}"]
                if orientation == "landscape":
                    options += ["-o", "orientation-requested=4"]
                else:
                    options += ["-o", "orientation-requested=3"]
                if fit_to_page:
                    options += ["-o", "fit-to-page"]
                cmd += options + [str(image_file)]
                proc = _run_cmd(cmd)
                if proc.returncode != 0:
                    return res500(f"Print failed: {(proc.stderr or proc.stdout or '').strip()}")
                job_id = ""
                m = re.search(r"request id is\s+(\S+)", proc.stdout or "")
                if m:
                    job_id = m.group(1)
                logger.info(f"Print job submitted: {job_id} printer={printer or 'default'} copies={copies}")
                return res200(data={"job_id": job_id})
            finally:
                if is_temp:
                    try:
                        image_file.unlink()
                    except Exception:
                        pass
        except FileNotFoundError as e:
            return res400(str(e))
        except Exception as e:
            logger.error(f"Error in print_image: {e}")
            return res500("Error in print_image")
