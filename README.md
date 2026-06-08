# Imaginator

Generate an image from a text prompt using Replicate's `bytedance/seedream-4.5` model.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set your Replicate API token:

   ```bash
   export REPLICATE_API_TOKEN=your-token
   ```

## Usage

```bash
python imaginator.py "a cinematic sunrise over a futuristic city" -o city.jpg
```

Optional flags:

- `--size` (default: `4K`)
- `--aspect-ratio` (default: `16:9`)
