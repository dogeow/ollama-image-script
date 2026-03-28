# Image Generator

Generate images with the Ollama CLI. Configuration is loaded from `prompts.json`.

## Setup

```bash
git clone https://github.com/dogeow/ollama-image-script.git
cd ollama-image-script

python3 -m venv .venv
source .venv/bin/activate

pip install -r rpg_map_bg/requirements.txt
```

Install Ollama separately, then make sure the image model is available:

```bash
ollama pull x/z-image-turbo
```

Edit `prompts.json` before running the generator.

## `prompts.json` Format

Examples:

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
```

Field reference:

| Field | Description | Default |
| ------ | ------ | -------- |
| `width` | Output image width | 512 |
| `height` | Output image height | 512 |
| `format` | Output format (`png`/`jpg`) | `png` |
| `remove_bg` | Whether to remove the background with `rembg` | `false` |
| `output_dir` | Output directory, relative to the current working directory | `output/<type>` |
| `items` | Image entries, each with `filename` and `prompt` | `[]` |

Notes:

- `ollama run` generates images at the model's default size. The script then center-crops and resizes the result to match `width` and `height`.
- If `output_dir` is omitted, files are written to `output/<type>`, where `<type>` is the top-level key in `prompts.json`.
- In each `items` entry, `filename` is optional. If omitted, the script generates names like `<type>_001`, `<type>_002`, or `<type>_00002`, based on the item index and total count.

## Usage

```bash
.venv/bin/python run.py all
.venv/bin/python run.py <type>
.venv/bin/python run.py <type> 5 10
```

## Environment Variables

- `OLLAMA_MODEL`: Image generation model. Default: `x/z-image-turbo`
- `DEFAULT_WIDTH`: Default output width when a type does not specify `width`. Default: `512`
- `DEFAULT_HEIGHT`: Default output height when a type does not specify `height`. Default: `512`
- `THERMAL_THRESHOLD`: Pause when the thermal level is greater than or equal to this value. Default: `1`
- `PAUSE_SECONDS`: Number of seconds to wait when the machine is too hot. Default: `90`

## Dependencies

- Python 3.9+
- Ollama
- `rembg` (optional, required only when `remove_bg` is `true`)

## Directory Structure

```plaintext
ollma-image-script/
├── README.md           # English documentation
├── README_zh.md        # Chinese documentation
├── run.py              # Entry script
├── prompts.json        # Configuration file
├── .gitignore
└── rpg_map_bg/         # Core module
    ├── __init__.py
    ├── __main__.py
    ├── config.py
    ├── generator.py
    ├── platform.py
    └── thermal.py
```
