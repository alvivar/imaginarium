#!/usr/bin/env python3
"""Convert text to speech using Replicate's inworld/realtime-tts-2."""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, Protocol, cast

import replicate

MODEL = "inworld/realtime-tts-2"
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

# The Replicate endpoint accepts only these language codes (schema enum),
# even though inworld-tts-2 natively supports 200+ via Inworld's own API.
LANGUAGES = (
    "auto",
    "en",
    "zh",
    "ja",
    "ko",
    "ru",
    "it",
    "es",
    "pt",
    "fr",
    "de",
    "pl",
    "nl",
    "hi",
    "he",
    "ar",
)
SAMPLE_RATES = (8000, 16000, 22050, 24000, 32000, 44100, 48000)
TEXT_NORMALIZATION = ("auto", "on", "off")

# Output file extension per audio format (ogg_opus lives in an .ogg container).
EXTENSIONS = {"mp3": "mp3", "wav": "wav", "ogg_opus": "ogg", "flac": "flac"}

# Steering cheat-sheet shown at the bottom of --help. See docs/tts-steering.md.
STEERING_HELP = """\
Steering: write instructions in English inside [brackets], before the words
they affect. Fully supported on this model (inworld-tts-2).

  emotion     [say excitedly]  [sound sad]  [sound terrified]
  volume      [very quiet]  [very loud]
  pitch       [say in a low tone]  [say in a high pitch]
  speed       [very fast]  [very slow]
  style       [whisper in a hushed style]  [sing joyfully]
  non-verbal  [laugh] [sigh] [breathe] [clear throat] [cough] [yawn]  (inline)
  emphasis    CAPITALIZE words to stress them
  pause       <break time="1s" />  (SSML)

Combine qualities in one tag for the most control:
  [say sadly with deliberate pauses in a low voice and hushed style]

See docs/tts-steering.md for the full guide."""


class Readable(Protocol):
    """Protocol for Replicate file-like outputs."""

    def read(self) -> bytes:
        """Return the generated audio bytes."""
        ...


def speech_text(value: str) -> str:
    """Validate the text against the schema's 2000-character limit."""
    if not value.strip():
        raise argparse.ArgumentTypeError("must not be empty")
    if len(value) > 2000:
        raise argparse.ArgumentTypeError("must be at most 2000 characters")
    return value


def bounded_float(low: float, high: float) -> Callable[[str], float]:
    """Build an argparse type that parses a float within [low, high]."""

    def parse(value: str) -> float:
        number = float(value)
        if not low <= number <= high:
            raise argparse.ArgumentTypeError(f"must be between {low} and {high}")
        return number

    return parse


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments mirroring the realtime-tts-2 input schema."""
    parser = argparse.ArgumentParser(
        description="Convert text to speech.",
        epilog=STEERING_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "text", type=speech_text, help="Text to speak (max 2000 characters)."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: <timestamp>.<format>).",
    )
    parser.add_argument(
        "--voice",
        default="Ashley",
        help="Preset voice name or custom cloned voice ID (default: Ashley).",
    )
    parser.add_argument(
        "--language",
        choices=LANGUAGES,
        default="auto",
        help="Language of the text; 'auto' detects it (default: auto).",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        choices=SAMPLE_RATES,
        default=48000,
        help="Audio sample rate in Hz (default: 48000).",
    )
    parser.add_argument(
        "--temperature",
        type=bounded_float(0, 2),
        default=0.0,
        help="Randomness 0-2; 0 uses the model default of 1.1 (default: 0).",
    )
    parser.add_argument(
        "--format",
        choices=EXTENSIONS,
        default="mp3",
        help="Output audio format (default: mp3).",
    )
    parser.add_argument(
        "--speaking-rate",
        type=bounded_float(0, 1.5),
        default=0.0,
        help="Speaking speed multiplier 0-1.5; 0 is normal speed (default: 0).",
    )
    parser.add_argument(
        "--text-normalization",
        choices=TEXT_NORMALIZATION,
        default="auto",
        help="Expand numbers, dates, and abbreviations before synthesis (default: auto).",
    )
    return parser.parse_args()


def build_input(args: argparse.Namespace) -> dict[str, object]:
    """Assemble the model input from the parsed arguments."""
    return {
        "text": args.text,
        "voice_id": args.voice,
        "language": args.language,
        "sample_rate": args.sample_rate,
        "temperature": args.temperature,
        "audio_format": args.format,
        "speaking_rate": args.speaking_rate,
        "text_normalization": args.text_normalization,
    }


def main() -> int:
    """Run the command-line interface."""
    args = parse_args()
    if args.output is None:
        args.output = Path(
            datetime.now().strftime(TIMESTAMP_FORMAT) + "." + EXTENSIONS[args.format]
        )

    output = cast("Readable", replicate.run(MODEL, input=build_input(args)))
    if output is None:
        raise RuntimeError("Replicate returned no audio.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output.read())
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
