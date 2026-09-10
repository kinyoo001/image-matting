"""打包路径兼容:PyInstaller one-dir 模式把只读资源放进 _internal/,
开发模式则都在 backend/ 下。用这两个函数代替裸相对路径。"""

import sys
from pathlib import Path


def is_frozen():
    return getattr(sys, "frozen", False)


def app_dir():
    """可写目录:打包后是 exe 所在目录(放 config.json/logs/data),
    开发模式是 backend/ 目录。"""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def resource_dir():
    """只读资源目录(hub_model/web/assets):打包后是 _internal/,
    开发模式是 backend/ 目录。"""
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return app_dir() / "_internal"
    return Path(__file__).resolve().parent.parent
