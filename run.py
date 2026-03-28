#!/usr/bin/env python3
"""通用图片生成器入口。

用法:
    python run.py all           # 生成所有类型
    python run.py <type>        # 生成指定类型
    python run.py <type> 1 10   # 生成指定类型的第1-10个

配置: 当前目录下的 prompts.json
"""
import sys
from pathlib import Path

# 找到 rpg_map_bg 模块（脚本所在目录）
SCRIPT_DIR = Path(__file__).parent.resolve()

# 如果 rpg_map_bg 在当前目录下，优先使用
if (SCRIPT_DIR / "rpg_map_bg").is_dir():
    sys.path.insert(0, str(SCRIPT_DIR))
else:
    # 否则尝试从 pip 安装的路径导入
    pass

try:
    from rpg_map_bg.__main__ import main
except ImportError:
    print("Error: 未找到 rpg_map_bg 模块。", file=sys.stderr)
    print("请确保 rpg_map_bg/ 目录与此脚本在同一目录，或已 pip install。", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
