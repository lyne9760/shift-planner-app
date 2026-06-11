#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 测试环境
print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")

# 尝试导入排班模块
sys.path.insert(0, os.path.dirname(__file__))

try:
    # 运行排班生成器
    exec(open('schedule_generator_v2.py').read())
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
