#!/usr/bin/env python3
"""Convert text to speech using Replicate's google/gemini-3.1-flash-tts."""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Protocol, cast
from urllib.parse import urlsplit

import replicate

MODEL = "google/gemini-3.1-flash-tts"
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

VOICES = (
    "Achernar", "Achird", "Algenib", "Algieba", "Alnilam", "Aoede", "Autonoe",
    "Callirrhoe", "Charon", "Despina", "Enceladus", "Erinome", "Fenrir", "Gacrux",
    "Iapetus", "Kore", "Laomedeia", "Leda", "Orus", "Pulcherrima", "Puck",
    "Rasalgethi", "Sadachbia", "Sadaltager", "Schedar", "Sulafat", "Umbriel",
    "Vindemiatrix", "Zephyr", "Zubenelgenubi",
)
LANGUAGE_CODES = (
    "af-ZA", "am-ET", "ar-001", "ar-EG", "az-AZ", "be-BY", "bg-BG", "bn-BD",
    "ca-ES", "ceb-PH", "cmn-CN", "cmn-tw", "cs-CZ", "da-DK", "de-DE", "el-GR",
    "en-AU", "en-GB", "en-IN", "en-US", "es-419", "es-ES", "es-MX", "et-EE",
    "eu-ES", "fa-IR", "fi-FI", "fil-PH", "fr-CA", "fr-FR", "gl-ES", "gu-IN",
    "he-IL", "hi-IN", "hr-HR", "ht-HT", "hu-HU", "hy-AM", "id-ID", "is-IS",
    "it-IT", "ja-JP", "jv-JV", "ka-GE", "kn-IN", "ko-KR", "kok-IN", "la-VA",
    "lb-LU", "lo-LA", "lt-LT", "lv-LV", "mai-IN", "mg-MG", "mk-MK", "ml-IN",
    "mn-MN", "mr-IN", "ms-MY", "my-MM", "nb-NO", "ne-NP", "nl-NL", "nn-NO",
    "or-IN", "pa-IN", "pl-PL", "ps-AF", "pt-BR", "pt-PT", "ro-RO", "ru-RU",
    "sd-IN", "si-LK", "sk-SK", "sl-SI", "sq-AL", "sr-RS", "sv-SE", "sw-KE",
    "ta-IN", "te-IN", "th-TH", "tr-TR", "uk-UA", "ur-PK", "vi-VN",
)
MAX_TEXT_BYTES = 4000

# Extra guidance shown at the bottom of --help.
MARKUP_HELP = """\
Markup: insert expressive tags inline in the text.
  [sigh]  [laughing]  [whispering]  [shouting]  [extremely fast]

Style: describe tone, pace, accent, and emotion with --style, e.g.
  --style "say this in a calm, professional tone"
  --style "speak with excitement and energy"

Voices (--voice, default Kore):
  Achernar Achird Algenib Algieba Alnilam Aoede Autonoe Callirrhoe
  Charon Despina Enceladus Erinome Fenrir Gacrux Iapetus Kore
  Laomedeia Leda Orus Pulcherrima Puck Rasalgethi Sadachbia Sadaltager
  Schedar Sulafat Umbriel Vindemiatrix Zephyr Zubenelgenubi

Languages: 87 BCP-47 codes (--language, default en-US). See README.md."""


class AudioOutput(Protocol):
    """Protocol for the Replicate file-like output (has a URL and bytes)."""

    url: str

    def read(self) -> bytes:
        """Return the generated audio bytes."""
        ...


def speech_text(value: str) -> str:
    """Validate the text against the schema's 4000-byte limit."""
    if not value.strip():
        raise argparse.ArgumentTypeError("must not be empty")
    if len(value.encode("utf-8")) > MAX_TEXT_BYTES:
        raise argparse.ArgumentTypeError(f"must be at most {MAX_TEXT_BYTES} bytes")
    return value


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments mirroring the gemini-3.1-flash-tts schema."""
    parser = argparse.ArgumentParser(
        description="Convert text to speech.",
        epilog=MARKUP_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("text", type=speech_text, help="Text to speak (max 4000 bytes).")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: <timestamp> with the returned format).",
    )
    parser.add_argument(
        "--voice",
        choices=VOICES,
        metavar="VOICE",
        default="Kore",
        help="Voice name; see the list below (default: Kore).",
    )
    parser.add_argument(
        "--style",
        default="Say the following.",
        help='Style/delivery instructions, the model\'s "prompt" field '
        '(default: "Say the following.").',
    )
    parser.add_argument(
        "--language",
        choices=LANGUAGE_CODES,
        metavar="CODE",
        default="en-US",
        help="BCP-47 language code, e.g. en-US, en-GB, es-ES, ja-JP (default: en-US).",
    )
    return parser.parse_args()


def build_input(args: argparse.Namespace) -> dict[str, object]:
    """Assemble the model input from the parsed arguments."""
    return {
        "text": args.text,
        "voice": args.voice,
        "prompt": args.style,
        "language_code": args.language,
    }


def main() -> int:
    """Run the command-line interface."""
    args = parse_args()
    output = cast("AudioOutput", replicate.run(MODEL, input=build_input(args)))
    if output is None:
        raise RuntimeError("Replicate returned no audio.")

    if args.output is None:
        suffix = Path(urlsplit(output.url).path).suffix or ".wav"
        args.output = Path(datetime.now().strftime(TIMESTAMP_FORMAT) + suffix)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output.read())
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
