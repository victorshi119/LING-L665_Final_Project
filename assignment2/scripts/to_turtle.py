"""Write Turtle files from the JSONL triple files."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import write_turtle


def main() -> None:
    for extractor in ("spacy", "llm"):
        path = write_turtle(extractor)
        print(path)


if __name__ == "__main__":
    main()
