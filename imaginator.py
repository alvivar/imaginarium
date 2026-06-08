#!/usr/bin/env python3
"""Generate an image from a text prompt using Replicate."""

import argparse
import sys
from pathlib import Path
from typing import Protocol

import replicate

MODEL = "bytedance/seedream-4.5"
DEFAULT_OUTPUT = "output.jpg"


class Readable(Protocol):
    """Protocol for Replicate file-like outputs."""

    def read(self) -> bytes:
        """Return the generated image bytes."""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate an image from a prompt.")
    parser.add_argument("prompt", help="Text description of the image.")
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        type=Path,
        help=f"Output file path (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument("--size", default="4K", help="Image size (e.g. 1K, 2K, 4K).")
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (e.g. 16:9).")
    return parser.parse_args()


def generate_image(prompt: str, size: str, aspect_ratio: str) -> bytes:
    """Generate an image and return its bytes."""
    output: list[Readable] = replicate.run(
        MODEL,
        input={
            "prompt": prompt,
            "size": size,
            "aspect_ratio": aspect_ratio,
        },
    )

    if not output:
        raise RuntimeError("Replicate returned no generated images.")

    return output[0].read()


def main() -> int:
    """Run the command-line interface."""
    args = parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(generate_image(args.prompt, args.size, args.aspect_ratio))

    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
