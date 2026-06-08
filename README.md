# Imaginator

A small collection of command-line tools for generating images with
[Replicate](https://replicate.com) models. Each model gets its own
self-contained script named after it; `seedream.py` is the first.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set your Replicate API token:

   ```bash
   export REPLICATE_API_TOKEN=your-token
   ```

## Tools

### `seedream.py`

Generate images with `bytedance/seedream-4.5`.

```bash
python seedream.py "a cinematic sunrise over a futuristic city"
```

By default the image is written to `<timestamp>.jpg`
(e.g. `2026-06-08_11-58-38.jpg`). Pass `-o NAME.jpg` to choose the name.

Optional flags:

- `-o`, `--output` — output path (default: `<YYYY-MM-DD_HH-MM-SS>.jpg`)
- `--size` — `2K`, `4K`, or `custom` (default: `2K`)
- `--aspect-ratio` — e.g. `1:1`, `16:9` (default: `match_input_image`; ignored with `--size custom`)
- `--width` / `--height` — 1024–4096, used only with `--size custom` (default: `2048`)
- `--image URI` — input image for image-to-image; a local path or URL, repeatable (1–14)
- `--sequential` — let the model generate multiple related images
- `--max-images` — 1–15, used with `--sequential` (default: `1`)
- `--safety-checker` — enable the safety checker (off by default)

When several images are produced, the output name is indexed:
`<name>_0.jpg`, `<name>_1.jpg`, …

### `upscale.py`

Upscale an image with `prunaai/p-image-upscale`.

```bash
python upscale.py input.jpg
python upscale.py https://example.com/photo.jpg --mode factor --factor 4
```

By default the result is written to `<timestamp>.<format>`. Pass `-o NAME`
to choose the name.

Optional flags:

- `-o`, `--output` — output path (default: `<YYYY-MM-DD_HH-MM-SS>.<format>`)
- `--mode` — `target` (scale to a megapixel resolution) or `factor` (multiply each side) (default: `target`)
- `--target` — target megapixels, 1–128, used with `--mode target` (default: `4`)
- `--factor` — per-side scaling factor, 1–8, used with `--mode factor` (default: `2`)
- `--format` — `webp`, `jpg`, or `png` (default: `jpg`)
- `--quality` — output quality 0–100, ignored for png (default: `80`)
- `--enhance-details` — enhance fine textures and small details
- `--enhance-realism` — improve realism; recommended for AI-generated images
- `--safety-checker` — enable the safety checker (off by default)

The input image may be a local path or a URL.
