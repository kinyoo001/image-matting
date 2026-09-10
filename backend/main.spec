# -*- mode: python ; coding: utf-8 -*-

import argparse
import importlib.util
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")
options, _ = parser.parse_known_args()

block_cipher = None

# tinify 单独打 christian 包容易漏,动态定位(找不到则跳过,由 Analysis 自动收集)
_tinify_datas = []
_tinify_spec = importlib.util.find_spec("tinify")
if _tinify_spec and _tinify_spec.submodule_search_locations:
    _tinify_datas = [(str(Path(_tinify_spec.submodule_search_locations[0])), "tinify")]

# 分析步骤，收集所需的文件和依赖项
a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
       ('./web', 'web'),  # 收集 web 目录
        ('./assets', 'assets'),
        ('config.json', '.'),
    ] + _tinify_datas,
    hiddenimports=['api', 'conf', 'hub_model', 'utilities', 'loguru'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 收集 hub_model,但排除 RMBG-2.0(约 1GB,走首次使用时下载,不打进包)
a.datas += Tree('./hub_model', prefix='hub_model', excludes=['RMBG-2.0', '__pycache__', '*.pyc'])

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 根据是否为调试模式设置不同的 EXE 和 COLLECT 参数
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ImageMatting",
    debug=options.debug,  # 设置调试模式
    bootloader_ignore_signals=False,
    strip=False,  # 非调试模式时移除符号表
    upx=not options.debug,  # 非调试模式时使用 UPX 压缩
    console=options.debug,  # 调试模式时显示控制台窗口
    disable_windowed_traceback=not options.debug,  # 非调试模式时禁用窗口化的回溯
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=not options.debug,  # 非调试模式时使用 UPX 压缩
    upx_exclude=[],
    name="小颖AI抠图_debug" if options.debug else "小颖AI抠图",
)
