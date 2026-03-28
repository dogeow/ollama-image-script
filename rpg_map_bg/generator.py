"""生成逻辑：调用 ollama CLI、查找新图、处理、保存。配置从 prompts.json 读取。"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from . import config
from .thermal import format_thermal_status, wait_if_hot


def _load_prompts():
    """从当前目录的 prompts.json 加载配置。"""
    prompts_path = Path("prompts.json")
    if not prompts_path.exists():
        print("Error: 未找到 prompts.json 配置文件。", file=sys.stderr)
        print("", file=sys.stderr)
        print("请创建 prompts.json 文件，例如：", file=sys.stderr)
        print("  cp prompts.json.example prompts.json", file=sys.stderr)
        print("", file=sys.stderr)
        print("或参考 prompts.json.example 创建自己的配置。", file=sys.stderr)
        sys.exit(1)
    with open(prompts_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_type_config(item_type: str):
    """获取指定类型的配置和项目列表。"""
    data = _load_prompts()
    type_data = data.get(item_type, {})
    cfg = {
        "width": type_data.get("width", config.DEFAULT_WIDTH),
        "height": type_data.get("height", config.DEFAULT_HEIGHT),
        "format": type_data.get("format", config.DEFAULT_FORMAT),
        "remove_bg": type_data.get("remove_bg", False),
        "output_dir": type_data.get("output_dir", item_type),
    }
    items = type_data.get("items", [])
    item_list = [(item["filename"], item["prompt"]) for item in items if "filename" in item and "prompt" in item]
    return cfg, item_list


def _get_output_dir(dir_name: str) -> Path:
    """根据 output_dir 获取输出路径。相对路径基于当前运行目录。"""
    path = Path(dir_name)
    if path.is_absolute():
        return path
    # 相对路径，在当前运行目录下创建
    return Path.cwd() / dir_name


def _save_image_file(outfile: Path, src: Path, img_format: str, width: int, height: int) -> None:
    """把已生成的图片文件按目标格式保存到 outfile。"""
    from PIL import Image, ImageOps

    target_format = "JPEG" if img_format.lower() in {"jpg", "jpeg"} else "PNG"
    with Image.open(src) as img:
        if img.size != (width, height):
            # 图像模型通常输出固定尺寸，这里做居中裁剪+缩放以匹配配置尺寸。
            img = ImageOps.fit(img, (width, height), method=Image.Resampling.LANCZOS)
        if target_format == "JPEG":
            if img.mode not in {"RGB", "L"}:
                img = img.convert("RGB")
            img.save(outfile, target_format, quality=95)
        else:
            img.save(outfile, target_format)


def _wait_for_stable_file(path: Path, timeout: float = 15.0, interval: float = 0.5) -> bool:
    """等待文件落盘稳定，避免拿到仍在写入中的图片。"""
    deadline = time.monotonic() + timeout
    last_size = -1
    stable_count = 0

    while time.monotonic() < deadline:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            time.sleep(interval)
            continue

        if size > 0 and size == last_size:
            stable_count += 1
            if stable_count >= 2:
                return True
        else:
            stable_count = 0
            last_size = size

        time.sleep(interval)

    return path.exists() and path.stat().st_size > 0


def _run_ollama_cli(prompt: str, width: int, height: int, cwd: Path, outfile: Path, img_format: str) -> tuple[bool, Optional[str]]:
    """通过 ollama CLI 单次调用生成图片，并从 cwd 中抓取最新落盘文件。"""
    created_after = time.time()
    try:
        result = subprocess.run(
            ["ollama", "run", config.OLLAMA_MODEL, prompt],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=config.OLLAMA_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return False, f"CLI 超时（>{config.OLLAMA_TIMEOUT}s）"
    except FileNotFoundError:
        return False, "未找到 ollama 命令"

    generated = _find_latest_image(
        cwd,
        exclude_prefix=outfile.stem,
        newer_than=created_after,
        max_retries=10,
        retry_delay=0.5,
    )
    if not generated:
        output = (result.stdout or "") + (result.stderr or "")
        output = output.strip()
        if len(output) > 600:
            output = output[-600:]
        if result.returncode != 0:
            return False, output or f"CLI 退出码 {result.returncode}"
        return False, output or "CLI 已退出，但未生成图片文件"

    if not _wait_for_stable_file(generated):
        return False, f"生成文件未稳定写入: {generated.name}"

    _save_image_file(outfile, generated, img_format, width, height)

    try:
        if generated.resolve() != outfile.resolve():
            generated.unlink(missing_ok=True)
    except Exception:
        pass

    return True, None


def check_ollama() -> bool:
    """检测 ollama CLI 是否已安装。"""
    return shutil.which("ollama") is not None


def require_ollama() -> None:
    """检测 ollama CLI 是否已安装；未检测到则打印提示并退出。"""
    if not check_ollama():
        print("Error: 未检测到 ollama。", file=sys.stderr)
        print("", file=sys.stderr)
        print("请先安装 ollama:", file=sys.stderr)
        print("  安装: https://ollama.com/download", file=sys.stderr)
        print("", file=sys.stderr)
        sys.exit(1)


def require_rembg() -> None:
    """检测 rembg 是否已安装；未安装则打印提示并退出。"""
    try:
        import rembg  # noqa: F401
    except ImportError:
        print("Error: remove_bg 需要 rembg 抠图（透明背景），未检测到 rembg。", file=sys.stderr)
        print("请先安装: pip install rembg", file=sys.stderr)
        sys.exit(1)


def _remove_bg(path: Path) -> bool:
    """用 rembg 去除背景，保存为带透明通道的 PNG。不依赖背景色，白底/黑底均可。"""
    try:
        from PIL import Image
        from rembg import remove as rembg_remove

        img = Image.open(path).convert("RGB")
        out = rembg_remove(img)
        out.save(path, "PNG")
        return True
    except ImportError:
        print("  -> WARN: rembg 未安装，跳过抠图。安装: pip install rembg")
        return False
    except Exception as e:
        print(f"  -> WARN: rembg 失败: {e}")
        return False


def _find_latest_image(
    work_dir: Path,
    exclude_prefix: str,
    newer_than: Optional[float] = None,
    extensions: tuple[str, ...] = (".png", ".jpg", ".jpeg"),
    max_retries: int = None,
    retry_delay: float = None,
) -> Optional[Path]:
    """在 work_dir 下找最新生成的图片（排除以 exclude_prefix 开头的）。
    
    如果找不到，会重试最多 max_retries 次（默认从 config 读取），每次间隔 retry_delay 秒。
    """
    max_retries = max_retries if max_retries is not None else config.MAX_RETRIES
    retry_delay = retry_delay if retry_delay is not None else config.RETRY_DELAY
    for attempt in range(max_retries):
        candidates = []
        for ext in extensions:
            for f in work_dir.glob(f"*{ext}"):
                if exclude_prefix and f.name.startswith(exclude_prefix):
                    continue
                if newer_than is not None and f.stat().st_mtime < newer_than:
                    continue
                if f.is_file():
                    candidates.append(f)
        if candidates:
            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return candidates[0]
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
    return None


def _run_ollama(prompt: str, width: int, height: int, cwd: Optional[Path] = None, outfile: Path = None, img_format: str = "png") -> bool:
    """直接通过 ollama CLI 生成指定尺寸的图片并保存。"""
    success, detail_text = _run_ollama_cli(prompt, width, height, cwd or outfile.parent, outfile, img_format)
    if success:
        return True

    detail = f" ({detail_text})" if detail_text else ""
    print(f"  -> ERROR: 生成失败，ollama CLI 未生成 {width}x{height} 的图片{detail}")
    return False


def _elapsed_fmt(seconds: int) -> str:
    if seconds >= 60:
        return f"{seconds // 60}m {seconds % 60}s"
    return f"{seconds}s"


def generate_by_type(item_type: str, start: int, end: int) -> None:
    """通用生成函数，根据类型从 prompts.json 读取配置并生成图片。"""
    cfg, items = _get_type_config(item_type)
    if not items:
        print(f"No items configured for type: {item_type}")
        return

    work_dir = _get_output_dir(cfg["output_dir"])
    work_dir.mkdir(parents=True, exist_ok=True)

    width, height = cfg["width"], cfg["height"]
    img_format = cfg["format"]
    remove_bg = cfg["remove_bg"]

    for i in range(start, end + 1):
        idx = i - 1
        if idx >= len(items):
            print(f"Skip {item_type} index {i} (no item configured)")
            continue

        filename, prompt = items[idx]
        outfile = work_dir / f"{filename}.{img_format}"

        if outfile.exists():
            print(f"Skip {outfile.name} (exists)")
            continue
        if not prompt:
            print(f"Skip {outfile.name} (no prompt)")
            continue

        wait_if_hot()
        print(f"[thermal] 生成前: {format_thermal_status()}")
        print(f"Generating {item_type} {i}/{end}: {outfile.name} ({width}x{height})")
        gen_start = int(time.time())
        success = _run_ollama(prompt, width, height, cwd=work_dir, outfile=outfile, img_format=img_format)
        gen_end = int(time.time())
        print(f"[thermal] 生成后: {format_thermal_status()}")

        if not success:
            print("  -> ERROR: 生成失败")
            continue

        # 生成成功，处理图片
        origin = outfile.with_stem(outfile.stem + "_origin")
        shutil.copy2(outfile, origin)

        # 需要抠图时去除背景
        if remove_bg:
            _remove_bg(outfile)

        print(f"  -> saved as {outfile}，耗时: {_elapsed_fmt(gen_end - gen_start)}")


def get_available_types() -> list[str]:
    """获取 prompts.json 中配置的所有可用类型。"""
    data = _load_prompts()
    return list(data.keys())
