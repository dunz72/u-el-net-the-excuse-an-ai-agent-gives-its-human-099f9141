#!/usr/bin/env python3
"""Copy the one-line excuse entry to the make.fun output folder.

Reads ``entry.txt`` next to this script and writes it, byte for byte,
to ``entry.txt`` inside the directory named by ``MAKEFUN_OUTPUT_DIR``.
When that variable is absent or blank, a local ``output`` folder next
to this file is used instead.

Standard library only. Deterministic: same input, same bytes, every run.
The copied line is validated (one line, non-empty, at most 200 chars)
and verified with a SHA-256 digest printed to stdout.
"""

import hashlib
import os
import sys
from pathlib import Path

ENTRY_NAME = "entry.txt"
ENV_VAR = "MAKEFUN_OUTPUT_DIR"
MAX_CHARS = 200


def source_path():
    """Return the entry.txt sitting next to this script."""
    return Path(__file__).resolve().parent / ENTRY_NAME


def read_entry(path):
    """Read the entry line, stripping only the trailing newline."""
    text = path.read_text(encoding="utf-8")
    if text.endswith("\n"):
        text = text[:-1]
    return text


def validate_entry(text):
    """Guard the line: non-empty, single line, at most 200 chars."""
    if not text:
        raise ValueError("entry line is empty")
    if text != text.strip():
        raise ValueError("entry line must not start or end with whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be exactly one line")
    if len(text) > MAX_CHARS:
        raise ValueError(
            "entry line must be at most %d characters, got %d"
            % (MAX_CHARS, len(text))
        )


def pick_output_root():
    """Return the folder that should hold the copied entry file."""
    configured = os.environ.get(ENV_VAR, "").strip()
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parent / "output"


def output_path(root):
    """Return the full path of the entry file under root."""
    return root / ENTRY_NAME


def prepare_folder(root):
    """Make sure the output folder exists, creating parents too."""
    root.mkdir(parents=True, exist_ok=True)


def write_entry(path, text):
    """Persist the entry line, terminated by a newline."""
    path.write_text(text + "\n", encoding="utf-8")


def digest(text):
    """Return the SHA-256 hex digest of the entry line's bytes."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def copy_entry():
    """Read, validate, copy the entry and return its digest."""
    text = read_entry(source_path())
    validate_entry(text)
    root = pick_output_root()
    prepare_folder(root)
    write_entry(output_path(root), text)
    return text, digest(text)


def main(argv=None):
    """Entry point: copy the excuse line and report its digest."""
    del argv  # unused; kept for a conventional signature
    text, sha = copy_entry()
    print("entry.txt: %d characters" % len(text))
    print("sha256: %s" % sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
