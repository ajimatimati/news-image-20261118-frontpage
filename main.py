#!/usr/bin/env python3
"""Deterministic Python 3.13 standard-library-only entrypoint for make.fun
competition news-image-20261118 ("Sum up 18 November's world news in one image").

Validates that the repository's entry.png is a complete PNG or JPEG image within
the 1 MiB (1,048,576 bytes) and 1024x1024 pixel caps, then writes identical
bytes to $MAKEFUN_OUTPUT_DIR/entry.png (defaulting to /output/entry.png).
"""

from __future__ import annotations

import hashlib
import os
import struct
import sys
import zlib
from pathlib import Path

SOURCE_IMAGE = Path(__file__).resolve().parent / "entry.png"
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
EXPECTED_BYTES = 472_462
EXPECTED_SHA256 = "6d05cb6bc9decfe4cf997719413d5693285ce6256da8950544bcc539594cf3ce"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"
JPEG_SOF_MARKERS = frozenset(
    {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
)


def parse_png_dimensions(data: bytes) -> tuple[int, int]:
    if not data.startswith(PNG_MAGIC) or len(data) < 33:
        raise ValueError("Invalid PNG header")

    offset = 8
    width = height = 0
    saw_ihdr = False
    saw_iend = False

    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        payload_start = offset + 8
        payload_end = payload_start + length
        crc_end = payload_end + 4
        if crc_end > len(data):
            raise ValueError(f"Truncated PNG chunk {chunk_type!r}")

        payload = data[payload_start:payload_end]
        expected_crc = struct.unpack(">I", data[payload_end:crc_end])[0]
        actual_crc = zlib.crc32(chunk_type + payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"Corrupt PNG CRC in chunk {chunk_type!r}")

        if chunk_type == b"IHDR":
            width, height = struct.unpack(">II", payload[:8])
            saw_ihdr = True
        elif chunk_type == b"IEND":
            saw_iend = True
            offset = crc_end
            break
        offset = crc_end

    if not saw_ihdr or not saw_iend:
        raise ValueError("Incomplete PNG image (missing IHDR or IEND)")
    return width, height


def parse_jpeg_dimensions(data: bytes) -> tuple[int, int]:
    if not data.startswith(JPEG_SOI) or not data.endswith(JPEG_EOI):
        raise ValueError("Invalid or incomplete JPEG image (SOI/EOI mismatch)")

    offset = 2
    n = len(data)
    while offset + 2 <= n:
        if data[offset] != 0xFF:
            raise ValueError(f"Malformed JPEG marker stream at byte {offset}")
        while offset < n and data[offset] == 0xFF:
            offset += 1
        if offset >= n:
            break
        marker = data[offset]
        offset += 1

        if marker == 0xD9:  # EOI
            break
        if marker in (0x01, 0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7):
            continue
        if marker == 0xDA:  # Start of Scan (entropy-coded payload follows)
            break

        if offset + 2 > n:
            raise ValueError("Truncated JPEG segment length")
        seg_len = struct.unpack(">H", data[offset : offset + 2])[0]
        if seg_len < 2 or offset + seg_len > n:
            raise ValueError(f"Invalid JPEG segment length {seg_len}")

        if marker in JPEG_SOF_MARKERS:
            if seg_len < 7:
                raise ValueError("Truncated JPEG SOF frame header")
            height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
            return width, height

        offset += seg_len

    raise ValueError("JPEG missing Start-Of-Frame dimension marker")


def validate_image(data: bytes) -> tuple[str, int, int, str]:
    size = len(data)
    if size == 0 or size > MAX_BYTES:
        raise ValueError(
            f"entry.png size {size} bytes is outside allowed range (1..{MAX_BYTES})"
        )

    if data.startswith(PNG_MAGIC):
        fmt = "PNG"
        width, height = parse_png_dimensions(data)
    elif data.startswith(JPEG_SOI):
        fmt = "JPEG"
        width, height = parse_jpeg_dimensions(data)
    else:
        raise ValueError("entry.png is neither a valid PNG nor JPEG image")

    if not (1 <= width <= MAX_DIMENSION and 1 <= height <= MAX_DIMENSION):
        raise ValueError(
            f"Image dimensions {width}x{height} exceed {MAX_DIMENSION}x{MAX_DIMENSION}"
        )
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ValueError(
            f"Unexpected image dimensions {width}x{height}; expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )

    digest = hashlib.sha256(data).hexdigest()
    if size != EXPECTED_BYTES or digest != EXPECTED_SHA256:
        raise ValueError(
            f"Integrity mismatch: got {size} bytes / {digest}, expected {EXPECTED_BYTES} bytes / {EXPECTED_SHA256}"
        )
    return fmt, width, height, digest


def main() -> int:
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "entry.png"

    data = SOURCE_IMAGE.read_bytes()
    fmt, width, height, digest = validate_image(data)

    tmp_destination = output_dir / ".entry.png.tmp"
    tmp_destination.write_bytes(data)
    tmp_destination.replace(destination)

    written = destination.read_bytes()
    if hashlib.sha256(written).hexdigest() != digest:
        raise RuntimeError("Output verification failed: SHA-256 mismatch after write")

    print(
        f"Verified {fmt} {width}x{height} ({len(data)} bytes, sha256={digest}) -> {destination}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
