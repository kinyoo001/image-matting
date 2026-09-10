#!/bin/bash
# 双击即用：启动小颖AI抠图桌面版
cd "$(dirname "$0")/backend" || exit 1
exec ./.venv-matting/bin/python main.py
