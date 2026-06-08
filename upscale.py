#!/usr/bin/env python3
"""Upscale an image using Replicate's prunaai/p-image-upscale."""

import argparse
import sys
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from typing import IO, Callable, Protocol, TypeVar, cast
from urllib.parse import urlsplit

import replicate

MODEL = "prunaai/p-image-upscale"
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

MODES = ("target", "factor")
FORMATS = ("webp", "jpg", "png")

ImageInput = str | IO[bytes]


class Readable(Protocol):
    """Protocol for Replicate file-like outputs."""

    def read(self) -> bytes:
        """Return the upscaled image bytes."""
        ...


N = TypeVar("N", int, float)


def bounded(convert: Callable[[str], N], low: N, high: N) -> Callable[[str], N]:
    """Build an argparse type that parses a number within [low, high]."""

    def parse(value: str) -> N:
        number = convert(value)
        if not low <= number <= high:
            raise argparse.ArgumentTypeError(f"must be between {low} and {high}")
        return number

    return parse


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments mirroring the p-image-upscale input schema."""
    parser = argparse.ArgumentParser(description="Upscale an image.")
    parser.add_argument("image", help="Input image to upscale (local path or URL).")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: <timestamp>.<format>).",
    )
    parser.add_argument(
        "--mode",
        choices=MODES,
        default="target",
        help="target scales to a megapixel resolution; factor multiplies each side (default: target).",
    )
    parser.add_argument(
        "--target",
        type=bounded(int, 1, 128),
        default=4,
        help="Target resolution in megapixels, 1-128, used with --mode target (default: 4).",
    )
    parser.add_argument(
        "--factor",
        type=bounded(float, 1, 8),
        default=2.0,
        help="Per-side scaling factor, 1-8, used with --mode factor (default: 2).",
    )
    parser.add_argument(
        "--format",
        choices=FORMATS,
        default="jpg",
        help="Output image format (default: jpg).",
    )
    parser.add_argument(
        "--quality",
        type=bounded(int, 0, 100),
        default=80,
        help="Output quality 0-100; ignored for png (default: 80).",
    )
    parser.add_argument(
        "--enhance-details",
        action="store_true",
        help="Enhance fine textures and small details.",
    )
    parser.add_argument(
        "--enhance-realism",
        action="store_true",
        help="Improve realism; recommended for AI-generated images.",
    )
    parser.add_argument(
        "--safety-checker",
        action="store_true",
        help="Enable the safety checker (off by default).",
    )
    return parser.parse_args()


def resolve_image(value: str, stack: ExitStack) -> ImageInput:
    """Open local paths as binary files for upload; pass URLs through unchanged."""
    path = Path(value).expanduser()
    if path.is_file():
        return stack.enter_context(path.open("rb"))
    if value.startswith(("http://", "https://")):
        return value
    raise SystemExit(f"error: image not found and not a URL: {value}")


def build_input(args: argparse.Namespace, image: ImageInput) -> dict[str, object]:
    """Assemble the model input, including only the field relevant to the chosen mode."""
    payload: dict[str, object] = {
        "image": image,
        "upscale_mode": args.mode,
        "output_format": args.format,
        "enhance_details": args.enhance_details,
        "enhance_realism": args.enhance_realism,
        "disable_safety_checker": not args.safety_checker,
    }
    if args.format != "png":
        payload["output_quality"] = args.quality
    if args.mode == "target":
        payload["target"] = args.target
    else:
        payload["factor"] = args.factor
    return payload


def default_output(image: str, output_format: str) -> Path:
    """Derive '<input-stem>_upscaled_<timestamp>.<format>' from the input path or URL."""
    source = (
        urlsplit(image).path if image.startswith(("http://", "https://")) else image
    )
    stem = Path(source).stem
    prefix = f"{stem}_upscaled" if stem else "upscaled"
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    return Path(f"{prefix}_{timestamp}.{output_format}")


def main() -> int:
    """Run the command-line interface."""
    args = parse_args()
    if args.output is None:
        args.output = default_output(args.image, args.format)

    with ExitStack() as stack:
        payload = build_input(args, resolve_image(args.image, stack))
        output = cast("Readable", replicate.run(MODEL, input=payload))
    if output is None:
        raise RuntimeError("Replicate returned no upscaled image.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output.read())
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
