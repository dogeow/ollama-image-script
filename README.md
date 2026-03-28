# Image Generator

Generate images with the Ollama CLI. Configuration is loaded from `prompts.json`.

## Usage

```bash
.venv/bin/python run.py all              # Generate all configured types
.venv/bin/python run.py <type>           # Generate all items for a specific type
.venv/bin/python run.py <type> 5 10      # Generate items 5 through 10 for a type
```

## `prompts.json` Format

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

Field reference:

| Field | Description | Default |
|------|------|--------|
| `width` | Output image width | 128 |
| `height` | Output image height | 128 |
| `format` | Output format (`png`/`jpg`) | `png` |
| `remove_bg` | Whether to remove the background with `rembg` | `false` |
| `output_dir` | Output directory, relative to the current working directory | Type name |
| `items` | Image entries, each with `filename` and `prompt` | `[]` |

Notes:

- `ollama run` generates images at the model's default size. The script then center-crops and resizes the result to match `width` and `height`.

## Environment Variables

- `OLLAMA_MODEL`: Image generation model. Default: `x/z-image-turbo`
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
├── prompts.json.example # Example configuration
├── .gitignore
└── rpg_map_bg/         # Core module
    ├── __init__.py
    ├── __main__.py
    ├── config.py
    ├── generator.py
    ├── platform.py
    └── thermal.py
```
