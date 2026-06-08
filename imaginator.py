#!/usr/bin/env python3
"""Generate an image from a text prompt using Replicate."""

import argparse
import sys

import replicate

MODEL = "bytedance/seedream-4.5"


def main():
    parser = argparse.ArgumentParser(description="Generate an image from a prompt.")
    parser.add_argument("prompt", help="Text description of the image.")
    parser.add_argument("-o", "--output", default="output.jpg", help="Output file path.")
    parser.add_argument("--size", default="4K", help="Image size (e.g. 1K, 2K, 4K).")
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (e.g. 16:9).")
    args = parser.parse_args()

    output = replicate.run(
        MODEL,
        input={
            "prompt": args.prompt,
            "size": args.size,
            "aspect_ratio": args.aspect_ratio,
        },
    )

    with open(args.output, "wb") as file:
        file.write(output[0].read())

    print(args.output)


if __name__ == "__main__":
    sys.exit(main())
