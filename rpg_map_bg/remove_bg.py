#!/usr/bin/env python3
"""单独使用 rembg 去除图片背景。"""
import argparse
from pathlib import Path

try:
    from PIL import Image
    from rembg import remove as rembg_remove
except ImportError:
    print("请先安装依赖: pip install rembg pillow")
    exit(1)


def remove_bg(input_path: Path, output_path: Path | None = None) -> bool:
    """用 rembg 去除背景，保存为带透明通道的 PNG。"""
    try:
        img = Image.open(input_path).convert("RGB")
        out = rembg_remove(img)

        if output_path is None:
            output_path = input_path.with_suffix(".png")

        out.save(output_path, "PNG")
        print(f"  -> 已保存: {output_path}")
        return True
    except Exception as e:
        print(f"  -> 失败: {e}")
        return False


def process_directory(dir_path: Path, prefix: str = "item_") -> None:
    """处理目录下所有图片。"""
    extensions = (".png", ".jpg", ".jpeg")
    for ext in extensions:
        for f in dir_path.glob(f"*{ext}"):
            if f.name.startswith(prefix):
                continue
            print(f"处理: {f.name}")
            remove_bg(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="用 rembg 去除图片背景")
    parser.add_argument("path", help="图片文件或目录路径")
    parser.add_argument("-o", "--output", help="输出文件路径（单文件时使用）")
    parser.add_argument("-p", "--prefix", default="item_", help="目录模式时排除的文件前缀")
    args = parser.parse_args()

    path = Path(args.path)

    if path.is_file():
        remove_bg(path, Path(args.output) if args.output else None)
    elif path.is_dir():
        process_directory(path, args.prefix)
    else:
        print(f"路径不存在: {path}")


if __name__ == "__main__":
    main()
