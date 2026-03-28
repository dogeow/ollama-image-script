# 图片生成器

用 Ollama CLI 生成图片，配置从 `prompts.json` 读取。

## 用法

```bash
.venv/bin/python run.py all              # 生成所有类型
.venv/bin/python  run.py <type>           # 生成指定类型全部
.venv/bin/python  run.py <type> 5 10      # 生成指定类型的第5-10个
```

## prompts.json 格式

```json
{
  "landscapes": {
    "width": 640,
    "height": 360,
    "format": "jpg",
    "remove_bg": false,
    "output_dir": "output/landscapes",
    "items": [
      {"filename": "scene1", "prompt": "a beautiful mountain..."},
      {"filename": "scene2", "prompt": "a dark forest..."}
    ]
  },
  "icons": {
    "width": 128,
    "height": 128,
    "format": "png",
    "remove_bg": true,
    "output_dir": "output/icons",
    "items": [
      {"filename": "icon1", "prompt": "a sword icon..."}
    ]
  }
}
```

字段说明：

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `width` | 图片宽度 | 128 |
| `height` | 图片高度 | 128 |
| `format` | 输出格式 (png/jpg) | png |
| `remove_bg` | 是否用 rembg 抠图 | false |
| `output_dir` | 输出目录（相对当前目录） | 类型名 |
| `items` | 图片列表，每个包含 `filename` 和 `prompt` | [] |

说明：

- `ollama run` 会按模型默认尺寸出图，脚本再按 `width` / `height` 做居中裁剪和缩放，得到最终输出尺寸。

## 环境变量

- `OLLAMA_MODEL`：生图模型（默认 `x/z-image-turbo`）
- `THERMAL_THRESHOLD`：热等级 ≥ 此值则暂停（默认 1）
- `PAUSE_SECONDS`：过热时每次暂停秒数（默认 90）

## 依赖

- Python 3.9+
- Ollama
- rembg（可选，`remove_bg` 为 true 时需要）

## 目录结构

```plaintext
ollma-image-script/
├── README.md
├── run.py              # 入口脚本
├── prompts.json.example # 配置示例
├── .gitignore
└── rpg_map_bg/         # 核心模块
    ├── __init__.py
    ├── __main__.py
    ├── config.py
    ├── generator.py
    ├── platform.py
    └── thermal.py
```
