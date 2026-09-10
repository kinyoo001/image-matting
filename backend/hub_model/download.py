import hashlib
import os
import sys
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent


def calculate_sha256(file_path):
    """计算文件的 SHA256 哈希值"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        # 逐块读取文件并更新哈希值
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def download_rmgb_onnx_model(expected_sha256):
    BASE_DIR = Path(".")
    mistral_models_path = BASE_DIR.joinpath("hub_model", "briaai", "RMBG-1.4")
    mistral_models_path.mkdir(parents=True, exist_ok=True)

    model_path = mistral_models_path.joinpath("model.onnx")
    if model_path.exists():
        print("RMBG-1.4 ONNX model already exists.")
        # 校验文件完整性
        calculated_sha256 = calculate_sha256(model_path)
        if calculated_sha256 == expected_sha256:
            print("File integrity check passed.")
        else:
            print(
                "File integrity check failed. Expected SHA256:",
                expected_sha256,
                "Calculated SHA256:",
                calculated_sha256,
            )
            # sha256 校验失败，删除文件
            print("Please delete the file and try again.")
        return

    print("Downloading RMBG-1.4 ONNX model...")
    # 优先 hf-mirror(国内快),失败则回退到 huggingface.co(海外 CI 稳)
    urls = [
        "https://hf-mirror.com/briaai/RMBG-1.4/resolve/main/onnx/model.onnx?download=true",
        "https://huggingface.co/briaai/RMBG-1.4/resolve/main/onnx/model.onnx",
    ]

    response = None
    last_error = None
    for url in urls:
        try:
            print(f"Trying {url.split('/')[2]} ...")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            if int(response.headers.get("content-length", 0)) > 10 * 1024 * 1024:
                break
            last_error = f"suspicious small file from {url}"
            response.close()
            response = None
        except Exception as e:
            last_error = f"{url}: {e}"
            response = None
    if response is None:
        raise RuntimeError(f"Failed to download RMBG-1.4 model. {last_error}")

    # 获取文件总大小
    total_size = int(response.headers.get("content-length", 0))
    downloaded_size = 0

    with open(model_path, "wb") as f:
        for data in response.iter_content(chunk_size=1024):
            f.write(data)  # 写入文件
            downloaded_size += len(data)  # 更新已下载的字节数

            # 计算下载进度
            progress = (downloaded_size / total_size) * 100
            print(f"\rDownloading: {progress:.2f}%", end="")  # 打印进度，不换行

    print("\nRMBG-1.4 ONNX model downloaded.")

    # 校验文件完整性
    calculated_sha256 = calculate_sha256(model_path)
    if calculated_sha256 == expected_sha256:
        print("File integrity check passed.")
    else:
        print(
            "File integrity check failed. Expected SHA256:",
            expected_sha256,
            "Calculated SHA256:",
            calculated_sha256,
        )


def download_rmbg2_onnx_model(token=None, expected_sha256=None):
    """下载 RMBG-2.0 ONNX 模型(约 800MB~1GB，需 HF token 且已接受模型协议)。"""
    BASE_DIR = Path(".")
    model_dir = BASE_DIR.joinpath("hub_model", "briaai", "RMBG-2.0")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir.joinpath("model.onnx")
    if model_path.exists():
        print("RMBG-2.0 ONNX model already exists.")
        if expected_sha256:
            calculated_sha256 = calculate_sha256(model_path)
            print(
                "File integrity check passed."
                if calculated_sha256 == expected_sha256
                else f"File integrity check FAILED: {calculated_sha256}"
            )
        return

    if not token:
        raise RuntimeError(
            "RMBG-2.0 is a gated model. Please accept the license at "
            "https://huggingface.co/briaai/RMBG-2.0 and retry with: "
            "HF_TOKEN=hf_xxx python hub_model/download.py rmbg-2.0"
        )

    print("Downloading RMBG-2.0 ONNX model (~800MB, please wait)...")
    url = "https://huggingface.co/briaai/RMBG-2.0/resolve/main/onnx/model.onnx"
    headers = {"Authorization": f"Bearer {token}"}

    with requests.get(url, stream=True, headers=headers) as response:
        if response.status_code in (401, 403):
            raise RuntimeError(
                f"Download denied (HTTP {response.status_code}). "
                "Check your token and that you have accepted the model license at "
                "https://huggingface.co/briaai/RMBG-2.0"
            )
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0
        with open(model_path, "wb") as f:
            for data in response.iter_content(chunk_size=1024 * 1024):
                if not data:
                    continue
                f.write(data)
                downloaded_size += len(data)
                if total_size:
                    progress = (downloaded_size / total_size) * 100
                    print(f"\rDownloading: {progress:.2f}%", end="")

    print("\nRMBG-2.0 ONNX model downloaded.")
    if expected_sha256:
        calculated_sha256 = calculate_sha256(model_path)
        print(
            "File integrity check passed."
            if calculated_sha256 == expected_sha256
            else f"File integrity check FAILED: {calculated_sha256}"
        )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rmbg-2.0":
        # RMBG-2.0 是 gated 仓库，需先在 HF 接受 CC BY-NC 协议，再用 token 下载:
        #   HF_TOKEN=hf_xxx python hub_model/download.py rmbg-2.0
        download_rmbg2_onnx_model(token=os.getenv("HF_TOKEN"))
    else:
        download_rmgb_onnx_model(
            "8cafcf770b06757c4eaced21b1a88e57fd2b66de01b8045f35f01535ba742e0f"
        )
