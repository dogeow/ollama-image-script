# 图片生成器

用 Ollama CLI 生成图片，配置从 `prompts.json` 读取。

## 安装

```bash
git clone <your-repo-url> ollama-image-script
cd ollama-image-script

python3 -m venv .venv
source .venv/bin/activate

pip install -r rpg_map_bg/requirements.txt
```

另外安装 Ollama，并确保图像模型已经拉取：

```bash
ollama pull x/z-image-turbo
```

运行前先按需修改 `prompts.json`。

## prompts.json 格式

示例：

```json
{
   "maps": {
    "items": [
      {
        "prompt": "RPG game background, safe training camp, green meadow with flowers"
      }
    ]
  },
  "landscapes": {
    "width": 640,
    "height": 360,
    "format": "jpg",
    "remove_bg": true,
    "output_dir": "landscapes",
    "items": [
      {"filename": "scene1", "prompt": "a beautiful mountain..."},
      {"filename": "scene2", "prompt": "a dark forest..."}
    ]
  }
}

字段说明：

| 字段 | 说明 | 默认值 |
| ------ | ------ | -------- |
| `width` | 图片宽度 | 512 |
| `height` | 图片高度 | 512 |
| `format` | 输出格式 (png/jpg) | png |
| `remove_bg` | 是否用 rembg 抠图 | false |
| `output_dir` | 输出目录（相对当前目录） | `output/<type>` |
| `items` | 图片列表，每个包含 `filename` 和 `prompt` | [] |

说明：

- `ollama run` 会按模型默认尺寸出图，脚本再按 `width` / `height` 做居中裁剪和缩放，得到最终输出尺寸。
- 如果不写 `output_dir`，输出目录默认是 `output/<type>`，其中 `<type>` 是 `prompts.json` 顶层的类型名。
- 每个 `items` 条目里的 `filename` 可以不写。不写时会按序号自动生成，例如 `<type>_001`、`<type>_002`，或在数量更大时生成 `<type>_00002`。


## 用法

```bash
.venv/bin/python run.py all
.venv/bin/python run.py <type>
.venv/bin/python run.py <type> 5 10
```

## 环境变量

- `OLLAMA_MODEL`：生图模型（默认 `x/z-image-turbo`）
- `DEFAULT_WIDTH`：当类型未设置 `width` 时使用的默认宽度（默认 `512`）
- `DEFAULT_HEIGHT`：当类型未设置 `height` 时使用的默认高度（默认 `512`）
- `THERMAL_THRESHOLD`：热等级 ≥ 此值则暂停（默认 1）
- `PAUSE_SECONDS`：过热时每次暂停秒数（默认 90）

## 依赖

- Python 3.9+
- Ollama
- rembg（可选，`remove_bg` 为 true 时需要）

## 目录结构

```plaintext
ollma-image-script/
├── README.md           # 英文文档
├── README_zh.md        # 中文文档
├── run.py              # 入口脚本
├── prompts.json        # 配置文件
├── .gitignore
└── rpg_map_bg/         # 核心模块
    ├── __init__.py
    ├── __main__.py
    ├── config.py
    ├── generator.py
    ├── platform.py
    └── thermal.py
```
