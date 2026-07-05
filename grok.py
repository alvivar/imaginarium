#!/usr/bin/env python3
"""Animate an image into a video using Replicate's xai/grok-imagine-video-1.5."""

import argparse
import sys
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from typing import IO, Callable, Protocol, cast

import replicate

MODEL = "xai/grok-imagine-video-1.5"
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

RESOLUTIONS = ("720p", "480p")
ASPECT_RATIOS = ("auto", "16:9", "4:3", "1:1", "9:16", "3:4", "3:2", "2:3")

MediaInput = str | IO[bytes]


class Readable(Protocol):
    """Protocol for Replicate file-like outputs."""

    def read(self) -> bytes:
        """Return the generated video bytes."""
        ...


def prompt_text(value: str) -> str:
    """Reject an empty or whitespace-only prompt."""
    if not value.strip():
        raise argparse.ArgumentTypeError("must not be empty")
    return value


def bounded_int(low: int, high: int) -> Callable[[str], int]:
    """Build an argparse type that parses an integer within [low, high]."""

    def parse(value: str) -> int:
        number = int(value)
        if not low <= number <= high:
            raise argparse.ArgumentTypeError(f"must be between {low} and {high}")
        return number

    return parse


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments mirroring the grok-imagine-video-1.5 input schema."""
    parser = argparse.ArgumentParser(description="Animate an image into a video.")
    parser.add_argument(
        "prompt", type=prompt_text, help="Text prompt describing the motion or scene."
    )
    parser.add_argument("image", help="Image to animate (local path or URL).")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: <timestamp>.mp4).",
    )
    parser.add_argument(
        "--duration",
        type=bounded_int(1, 15),
        default=5,
        help="Video duration in seconds, 1 to 15 (default: 5).",
    )
    parser.add_argument(
        "--resolution",
        choices=RESOLUTIONS,
        default="720p",
        help="Video resolution (default: 720p).",
    )
    parser.add_argument(
        "--aspect-ratio",
        choices=ASPECT_RATIOS,
        default="auto",
        help="Output aspect ratio; 'auto' uses the image's native ratio (default: auto).",
    )
    return parser.parse_args()


def resolve_media(value: str, stack: ExitStack) -> MediaInput:
    """Open local paths as binary files for upload; pass URLs through unchanged."""
    path = Path(value).expanduser()
    if path.is_file():
        return stack.enter_context(path.open("rb"))
    if value.startswith(("http://", "https://")):
        return value
    raise SystemExit(f"error: image not found and not a URL: {value}")


def build_input(args: argparse.Namespace, image: MediaInput) -> dict[str, object]:
    """Assemble the model input from the parsed arguments."""
    return {
        "prompt": args.prompt,
        "image": image,
        "duration": args.duration,
        "resolution": args.resolution,
        "aspect_ratio": args.aspect_ratio,
    }


def main() -> int:
    """Run the command-line interface."""
    args = parse_args()
    if args.output is None:
        args.output = Path(datetime.now().strftime(TIMESTAMP_FORMAT) + ".mp4")

    with ExitStack() as stack:
        payload = build_input(args, resolve_media(args.image, stack))
        # Grok rejects Replicate's uploaded-file URLs (they resolve to JSON metadata),
        # so send local files inline as base64 data URIs; remote URLs pass through unchanged.
        output = cast(
            "Readable",
            replicate.run(MODEL, input=payload, file_encoding_strategy="base64"),
        )
    if output is None:
        raise RuntimeError("Replicate returned no video.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output.read())
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
