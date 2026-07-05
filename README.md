# Imaginator

A small collection of command-line tools for generating and upscaling images
and video with [Replicate](https://replicate.com) models.

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
- `--image URI` — input image for image-to-image; a local path or URL, repeatable up to 14 times
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

By default the result is written to `<input-stem>_upscaled_<timestamp>.<format>`
in the current directory
(e.g. `photo.jpg` → `photo_upscaled_2026-06-08_13-07-57.jpg`). Pass `-o NAME`
to choose the name.

Optional flags:

- `-o`, `--output` — output path (default: `<input-stem>_upscaled_<YYYY-MM-DD_HH-MM-SS>.<format>`)
- `--mode` — `target` (scale to a megapixel resolution) or `factor` (multiply each side) (default: `target`)
- `--target` — target megapixels, 1–128, used with `--mode target` (default: `4`)
- `--factor` — per-side scaling factor, 1–8, used with `--mode factor` (default: `2`)
- `--format` — `webp`, `jpg`, or `png` (default: `jpg`)
- `--quality` — output quality 0–100, ignored for png (default: `80`)
- `--enhance-details` — enhance fine textures and small details
- `--enhance-realism` — improve realism; recommended for AI-generated images
- `--safety-checker` — enable the safety checker (off by default)

The input image may be a local path or a URL.

### `seedance.py`

Generate a video from a text prompt with `bytedance/seedance-2.0`.

```bash
python seedance.py "a cat surfing a wave at sunset"
python seedance.py "she says \"hello\"" --image first.jpg --resolution 1080p --duration 8
```

By default the video is written to `<timestamp>.mp4` in the current directory.
Pass `-o NAME.mp4` to choose the name.

Optional flags:

- `-o`, `--output` — output path (default: `<YYYY-MM-DD_HH-MM-SS>.mp4`)
- `--seed` — random seed for reproducible generation
- `--image` — first-frame image for image-to-video (local path or URL)
- `--last-frame` — last-frame image; requires `--image` (local path or URL)
- `--duration` — seconds, -1 to 15; `-1` lets the model choose (default: `5`)
- `--resolution` — `480p`, `720p`, `1080p`, or `4k` (default: `720p`)
- `--aspect-ratio` — `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9`, `9:21`, or `adaptive` (default: `16:9`)
- `--no-audio` — disable synchronized audio generation (on by default)
- `--reference-image` — reference image for character/style, repeatable up to 9
- `--reference-video` — reference video for motion/style, repeatable up to 3
- `--reference-audio` — reference audio for lip-sync, repeatable up to 3

Reference images/videos cannot be combined with `--image`/`--last-frame`, and
reference audio requires at least one reference image or video. All media
inputs may be local paths or URLs.
