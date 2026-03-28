"""配置：环境变量和默认参数。"""
import os

# ollama 生图模型
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "x/z-image-turbo")

# ollama 超时时间（秒）
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "600"))

# 热检测：>= 此值则暂停（0=正常，1+=过热）
THERMAL_THRESHOLD = int(os.environ.get("THERMAL_THRESHOLD", "1"))
# 过热时每次暂停秒数
PAUSE_SECONDS = int(os.environ.get("PAUSE_SECONDS", "90"))

# 等待文件生成：最大重试次数、间隔（秒）
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "600"))
RETRY_DELAY = float(os.environ.get("RETRY_DELAY", "1.0"))

# 默认图片参数
DEFAULT_WIDTH = int(os.environ.get("DEFAULT_WIDTH", "128"))
DEFAULT_HEIGHT = int(os.environ.get("DEFAULT_HEIGHT", "128"))
DEFAULT_FORMAT = os.environ.get("DEFAULT_FORMAT", "png")
