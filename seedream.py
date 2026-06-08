#!/usr/bin/env python3
"""Generate images from a text prompt using Replicate's Seedream 4.5."""

import argparse
import sys
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from typing import IO, Callable, Protocol, cast

import replicate

MODEL = "bytedance/seedream-4.5"
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

ImageInput = str | IO[bytes]

SIZES = ("2K", "4K", "custom")
ASPECT_RATIOS = (
    "match_input_image",
    "1:1",
    "4:3",
    "3:4",
    "4:5",
    "5:4",
    "16:9",
    "9:16",
    "3:2",
    "2:3",
    "21:9",
    "9:21",
)


class Readable(Protocol):
    """Protocol for Replicate file-like outputs."""

    def read(self) -> bytes:
        """Return the generated image bytes."""
        ...


def bounded_int(low: int, high: int) -> Callable[[str], int]:
    """Build an argparse type that parses an int within [low, high]."""

    def parse(value: str) -> int:
        number = int(value)
        if not low <= number <= high:
            raise argparse.ArgumentTypeError(f"must be between {low} and {high}")
        return number

    return parse


def prompt_text(value: str) -> str:
    """Validate the prompt against the schema's 4000-character limit."""
    if not value.strip():
        raise argparse.ArgumentTypeError("must not be empty")
    if len(value) > 4000:
        raise argparse.ArgumentTypeError("must be at most 4000 characters")
    return value


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments mirroring the Seedream 4.5 input schema."""
    parser = argparse.ArgumentParser(description="Generate images from a prompt.")
    parser.add_argument(
        "prompt", type=prompt_text, help="Text prompt (max 4000 chars)."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path; indexed when multiple (default: <timestamp>.jpg).",
    )
    parser.add_argument(
        "--size",
        choices=SIZES,
        default="2K",
        help="2K (2048px), 4K (4096px), or custom (default: 2K).",
    )
    parser.add_argument(
        "--aspect-ratio",
        choices=ASPECT_RATIOS,
        default="match_input_image",
        help="Aspect ratio; ignored when --size custom (default: match_input_image).",
    )
    parser.add_argument(
        "--width",
        type=bounded_int(1024, 4096),
        default=2048,
        help="Custom width 1024-4096, used only with --size custom (default: 2048).",
    )
    parser.add_argument(
        "--height",
        type=bounded_int(1024, 4096),
        default=2048,
        help="Custom height 1024-4096, used only with --size custom (default: 2048).",
    )
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        metavar="URI",
        dest="image_input",
        help="Input image URI for image-to-image; repeatable (1-14 images).",
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Let the model generate multiple related images (story/variations).",
    )
    parser.add_argument(
        "--max-images",
        type=bounded_int(1, 15),
        default=1,
        help="Max images when --sequential is set, 1-15 (default: 1).",
    )
    parser.add_argument(
        "--safety-checker",
        action="store_true",
        help="Enable the safety checker (off by default).",
    )
    args = parser.parse_args()
    if len(args.image_input) > 14:
        parser.error("--image may be given at most 14 times")
    return args


def resolve_image(value: str, stack: ExitStack) -> ImageInput:
    """Open local paths as binary files for upload; pass URLs through unchanged."""
    path = Path(value).expanduser()
    if path.is_file():
        return stack.enter_context(path.open("rb"))
    if value.startswith(("http://", "https://")):
        return value
    raise SystemExit(f"error: image not found and not a URL: {value}")


def build_input(
    args: argparse.Namespace, image_input: list[ImageInput]
) -> dict[str, object]:
    """Assemble the model input, including only fields relevant to the chosen size."""
    payload: dict[str, object] = {
        "prompt": args.prompt,
        "size": args.size,
        "image_input": image_input,
        "disable_safety_checker": not args.safety_checker,
        "sequential_image_generation": "auto" if args.sequential else "disabled",
    }
    if args.sequential:
        payload["max_images"] = args.max_images
    if args.size == "custom":
        payload["width"] = args.width
        payload["height"] = args.height
    else:
        payload["aspect_ratio"] = args.aspect_ratio
    return payload


def output_paths(base: Path, count: int) -> list[Path]:
    """Return one path per image, indexing the stem when there are several."""
    if count == 1:
        return [base]
    return [base.with_stem(f"{base.stem}_{i}") for i in range(count)]


def main() -> int:
    """Run the command-line interface."""
    args = parse_args()
    if args.output is None:
        args.output = Path(datetime.now().strftime(TIMESTAMP_FORMAT) + ".jpg")

    with ExitStack() as stack:
        images = [resolve_image(value, stack) for value in args.image_input]
        payload = build_input(args, images)
        output = cast("list[Readable]", replicate.run(MODEL, input=payload))
    if not output:
        raise RuntimeError("Replicate returned no generated images.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    for path, item in zip(output_paths(args.output, len(output)), output):
        path.write_bytes(item.read())
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
