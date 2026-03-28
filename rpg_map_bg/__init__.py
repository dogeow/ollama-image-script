# 用 ollama 生成图片，配置从 prompts.json 读取
from .generator import generate_by_type, get_available_types, require_rembg

__all__ = ["generate_by_type", "get_available_types", "require_rembg"]
