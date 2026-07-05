#!/usr/bin/env python3
"""Generate a video from a text prompt using Replicate's bytedance/seedance-2.0."""

import argparse
import sys
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from typing import IO, Callable, Protocol, cast

import replicate

MODEL = "bytedance/seedance-2.0"
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

RESOLUTIONS = ("480p", "720p", "1080p", "4k")
ASPECT_RATIOS = ("16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "9:21", "adaptive")

MAX_REFERENCE_IMAGES = 9
MAX_REFERENCE_VIDEOS = 3
MAX_REFERENCE_AUDIOS = 3

MediaInput = str | IO[bytes]


class Readable(Protocol):
    """Protocol for Replicate file-like outputs."""

    def read(self) -> bytes:
        """Return the generated video bytes."""
        ...


def prompt_text(value: str) -> str:
    """Validate the prompt against the schema's 4000-character limit."""
    if not value.strip():
        raise argparse.ArgumentTypeError("must not be empty")
    if len(value) > 4000:
        raise argparse.ArgumentTypeError("must be at most 4000 characters")
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
    """Parse command-line arguments mirroring the seedance-2.0 input schema."""
    parser = argparse.ArgumentParser(description="Generate a video from a text prompt.")
    parser.add_argument("prompt", type=prompt_text, help="Text prompt (max 4000 characters).")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: <timestamp>.mp4).",
    )
    parser.add_argument("--seed", type=int, help="Random seed for reproducible generation.")
    parser.add_argument(
        "--image",
        help="First-frame image for image-to-video (local path or URL).",
    )
    parser.add_argument(
        "--last-frame",
        help="Last-frame image; requires --image (local path or URL).",
    )
    parser.add_argument(
        "--duration",
        type=bounded_int(-1, 15),
        default=5,
        help="Video duration in seconds, -1 to 15; -1 lets the model choose (default: 5).",
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
        default="16:9",
        help="Video aspect ratio; 'adaptive' lets the model choose (default: 16:9).",
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable synchronized audio generation (on by default).",
    )
    parser.add_argument(
        "--reference-image",
        action="append",
        default=[],
        metavar="URI",
        help=f"Reference image for character/style, repeatable up to {MAX_REFERENCE_IMAGES} (local path or URL).",
    )
    parser.add_argument(
        "--reference-video",
        action="append",
        default=[],
        metavar="URI",
        help=f"Reference video for motion/style, repeatable up to {MAX_REFERENCE_VIDEOS} (local path or URL).",
    )
    parser.add_argument(
        "--reference-audio",
        action="append",
        default=[],
        metavar="URI",
        help=f"Reference audio for lip-sync, repeatable up to {MAX_REFERENCE_AUDIOS} (local path or URL).",
    )
    args = parser.parse_args()

    if args.last_frame and not args.image:
        parser.error("--last-frame requires --image")
    if (args.image or args.last_frame) and args.reference_image:
        parser.error("--image/--last-frame cannot be combined with --reference-image")
    if args.reference_audio and not (args.reference_image or args.reference_video):
        parser.error("--reference-audio requires at least one --reference-image or --reference-video")
    for values, limit, name in (
        (args.reference_image, MAX_REFERENCE_IMAGES, "--reference-image"),
        (args.reference_video, MAX_REFERENCE_VIDEOS, "--reference-video"),
        (args.reference_audio, MAX_REFERENCE_AUDIOS, "--reference-audio"),
    ):
        if len(values) > limit:
            parser.error(f"{name} may be given at most {limit} times")
    return args


def resolve_media(value: str, stack: ExitStack) -> MediaInput:
    """Open local paths as binary files for upload; pass URLs through unchanged."""
    path = Path(value).expanduser()
    if path.is_file():
        return stack.enter_context(path.open("rb"))
    if value.startswith(("http://", "https://")):
        return value
    raise SystemExit(f"error: media not found and not a URL: {value}")


def build_input(
    args: argparse.Namespace,
    image: MediaInput | None,
    last_frame: MediaInput | None,
    reference_images: list[MediaInput],
    reference_videos: list[MediaInput],
    reference_audios: list[MediaInput],
) -> dict[str, object]:
    """Assemble the model input, including optional fields only when provided."""
    payload: dict[str, object] = {
        "prompt": args.prompt,
        "duration": args.duration,
        "resolution": args.resolution,
        "aspect_ratio": args.aspect_ratio,
        "generate_audio": not args.no_audio,
    }
    if args.seed is not None:
        payload["seed"] = args.seed
    if image is not None:
        payload["image"] = image
    if last_frame is not None:
        payload["last_frame_image"] = last_frame
    if reference_images:
        payload["reference_images"] = reference_images
    if reference_videos:
        payload["reference_videos"] = reference_videos
    if reference_audios:
        payload["reference_audios"] = reference_audios
    return payload


def main() -> int:
    """Run the command-line interface."""
    args = parse_args()
    if args.output is None:
        args.output = Path(datetime.now().strftime(TIMESTAMP_FORMAT) + ".mp4")

    with ExitStack() as stack:
        image = resolve_media(args.image, stack) if args.image else None
        last_frame = resolve_media(args.last_frame, stack) if args.last_frame else None
        reference_images = [resolve_media(v, stack) for v in args.reference_image]
        reference_videos = [resolve_media(v, stack) for v in args.reference_video]
        reference_audios = [resolve_media(v, stack) for v in args.reference_audio]
        payload = build_input(
            args, image, last_frame, reference_images, reference_videos, reference_audios
        )
        output = cast("Readable", replicate.run(MODEL, input=payload))
    if output is None:
        raise RuntimeError("Replicate returned no video.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output.read())
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
