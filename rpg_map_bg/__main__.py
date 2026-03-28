"""CLI：通用图片生成器，配置从 prompts.json 读取。"""
import argparse
import platform as plat_module
import sys

from . import config
from .generator import generate_by_type, get_available_types, require_ollama, require_rembg, _get_type_config
from .platform import get_platform


def _parse_args() -> argparse.Namespace:
    available_types = get_available_types()
    type_list = "|".join(available_types) if available_types else "type1|type2"
    
    parser = argparse.ArgumentParser(
        description="用 ollama 生成图片，配置从 prompts.json 读取。",
        epilog=f"""
示例:
  全部:   python run.py all
  指定类型: python run.py <type> [start [end]]
  
可用类型: {type_list}

环境变量: OLLAMA_MODEL, THERMAL_THRESHOLD, PAUSE_SECONDS
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "type_or_all",
        nargs="?",
        default=available_types[0] if available_types else None,
        help=f"类型: all|{type_list}",
    )
    parser.add_argument("start", nargs="?", type=int, help="起始序号 (默认: 1)")
    parser.add_argument("end", nargs="?", type=int, help="结束序号 (默认: 该类型全部)")
    args = parser.parse_args()

    type_raw = args.type_or_all.lower()
    available = get_available_types()
    
    if type_raw == "all":
        args.type = "all"
    elif type_raw in available:
        args.type = type_raw
    else:
        # 尝试模糊匹配
        matches = [t for t in available if t.startswith(type_raw) or type_raw in t]
        if len(matches) == 1:
            args.type = matches[0]
        elif len(matches) > 1:
            print(f"模糊匹配到多个类型: {matches}，请明确指定", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"未知类型: {type_raw}，可用类型: {available}", file=sys.stderr)
            sys.exit(1)

    # 解析 start/end
    if args.type != "all":
        _, items = _get_type_config(args.type)
        total = len(items)
        args.start = args.start if args.start is not None else 1
        args.end = args.end if args.end is not None else total
    
    return args


def main() -> None:
    # 首先检测 ollama
    require_ollama()
    
    args = _parse_args()

    print(f"[platform] 当前: {get_platform()}")
    if plat_module.machine() == "arm64":
        print("[thermal] 热等级参考(°C)：0 Nominal <~65，1 Moderate ~65–80，2 Heavy ~80–95，3 Critical >95")
    print()

    if args.type == "all":
        # 检查是否有需要 rembg 的类型
        for type_name in get_available_types():
            cfg, _ = _get_type_config(type_name)
            if cfg.get("remove_bg", False):
                require_rembg()
                break
        # 依次生成所有类型
        for type_name in get_available_types():
            _, items = _get_type_config(type_name)
            if items:
                generate_by_type(type_name, 1, len(items))
    else:
        cfg, _ = _get_type_config(args.type)
        if cfg.get("remove_bg", False):
            require_rembg()
        generate_by_type(args.type, args.start, args.end)

    print("Done.")


if __name__ == "__main__":
    main()
