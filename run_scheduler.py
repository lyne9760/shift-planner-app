#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import importlib.util
import subprocess
import sys

print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")

script_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(script_dir, "scheduler_cp.py")

try:
    if importlib.util.find_spec("ortools") is None:
        print("缺少 OR-Tools。请先使用当前 Python 运行：python -m pip install -r requirements.txt")
        raise SystemExit(2)
    completed = subprocess.run([sys.executable, script_path, *sys.argv[1:]], check=False)
    raise SystemExit(completed.returncode)
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
