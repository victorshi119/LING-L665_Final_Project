#!/usr/bin/env python3

"""
build_arxiv_corpus.py

Merge arXiv metadata with the Docling/spaCy Layout Markdown and write one
cleaned JSONL corpus plus summary statistics.

Cleaning (from a survey of the 321 converted papers):
  - drop "<!-- image -->" placeholders
  - unescape HTML entities (&amp; &lt; &#8211; ...)
  - re-attach LaTeX diacritics that PDF extraction splits off their letter
    ("N¨oth" -> "Nöth", "Garc´ıa" -> "García", "Bj ¨orn" -> "Björn")
  - cut the References/Bibliography section and drop Acknowledgements
  - NFC-normalize and collapse runs of blank lines
U+FFFD characters (glyphs the PDF font could not map) cannot be recovered;
they are counted per paper in "n_replacement_chars".

Usage (needs spaCy for token counts; the spacy-layout env has it):
    source envs/spacy-layout/bin/activate
    python code/processing/build_arxiv_corpus.py data/raw/arxiv data/processed
"""


import argparse
import collections
import datetime
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

import spacy

# Spacing diacritics as emitted by PDF text extraction -> combining marks.
COMBINING = {"¨": "̈",   # ¨ diaeresis
             "´": "́",   # ´ acute
             "ˆ": "̂",   # ˆ circumflex
             "˜": "̃",   # ˜ tilde
             "ˇ": "̌",   # ˇ caron
             "˚": "̊",   # ˚ ring
             "¸": "̧",   # ¸ cedilla
             "˘": "̆"}   # ˘ breve
# Optional space before the mark is only swallowed inside a word ("Bj ¨orn"),
# i.e. lowercase on both sides; "Pablo ´Alvarez" keeps its space.
DIACRITIC = re.compile(r"(?:(?<=[a-z]) (?=[%s][a-zı]))?([%s])([A-Za-zıȷ])"
                       % ((re.escape("".join(COMBINING)),) * 2))

REFERENCES = re.compile(r"^#+\s*(?:[0-9IVX]+\.?\s*)?(references?|bibliography|literature cited)\s*$",
                        re.IGNORECASE | re.MULTILINE)
ACKNOWLEDGEMENTS = re.compile(r"^#+\s*(?:[0-9IVX]+\.?\s*)?acknowledge?ments?\s*$",
                              re.IGNORECASE | re.MULTILINE)
HEADING = re.compile(r"^#+\s", re.MULTILINE)


def fix_diacritics(text):
    def compose(match):
        mark, letter = match.group(1), match.group(2)
        base = {"ı": "i", "ȷ": "j"}.get(letter, letter)
        combined = unicodedata.normalize("NFC", base + COMBINING[mark])
        # Leave the text alone if no precomposed character exists.
        return combined if len(combined) == 1 else match.group(0)
    return DIACRITIC.sub(compose, text)


def strip_back_matter(text):
    """Cut at the last References heading; drop Acknowledgements.

    Headings in the first 15% are ignored so a thesis's table of contents
    entry cannot truncate the document. The threshold is low because long
    reference lists can make up most of a short paper's extracted text.
    """
    cut = None
    for match in REFERENCES.finditer(text):
        if match.start() > len(text) * 0.15:
            cut = match.start()
    removed_references = cut is not None
    if removed_references:
        text = text[:cut]
    while True:
        match = ACKNOWLEDGEMENTS.search(text)
        if not match:
            break
        following = HEADING.search(text, match.end())
        text = text[:match.start()] + (text[following.start():] if following else "")
    return text, removed_references


def clean(markdown):
    text = markdown.replace("<!-- image -->", "")
    text = html.unescape(text)
    text = fix_diacritics(text)
    text = unicodedata.normalize("NFC", text)
    text, removed_references = strip_back_matter(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, removed_references


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    parser.add_argument("raw_dir", type=Path, help="scraper output (metadata.jsonl, pdfs/)")
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--name", default="arxiv_corpus", help="output file stem")
    args = parser.parse_args()

    with open(args.raw_dir / "metadata.jsonl", encoding="utf-8") as fp:
        papers = [json.loads(line) for line in fp if line.strip()]

    tokenizer = spacy.blank("en").tokenizer
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / f"{args.name}.jsonl"

    stats = collections.Counter()
    licenses = collections.Counter()
    missing, flagged = [], []
    with open(out_path, encoding="utf-8", mode="w") as out:
        for paper in papers:
            md_path = args.raw_dir / "pdfs" / (paper["arxiv_id"].replace("/", "_") + ".md")
            if not md_path.exists():
                missing.append(paper["arxiv_id"])
                continue
            text, removed_references = clean(md_path.read_text(encoding="utf-8"))
            n_tokens = len(tokenizer(text))
            lowered = text.lower()
            record = {"id": f"arxiv:{paper['arxiv_id']}",
                      "source": "arxiv",
                      "arxiv_id": paper["arxiv_id"],
                      "version": paper["version"],
                      "title": paper["title"],
                      "abstract": paper["abstract"],
                      "authors": paper["authors"],
                      "published": paper["published"],
                      "primary_category": paper["primary_category"],
                      "categories": paper["categories"],
                      "doi": paper["doi"],
                      "journal_ref": paper["journal_ref"],
                      "license": paper["license"],
                      "url": paper["abs_url"],
                      "matched_queries": paper["matched_queries"],
                      "mentions_cerebral_palsy": "cerebral palsy" in lowered,
                      "mentions_dysarthria": "dysarthri" in lowered,
                      "references_removed": removed_references,
                      "n_replacement_chars": text.count("�"),
                      "n_chars": len(text),
                      "n_tokens": n_tokens,
                      "text": text}
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

            stats["documents"] += 1
            stats["tokens"] += n_tokens
            stats["chars"] += len(text)
            stats["mentions_cerebral_palsy"] += record["mentions_cerebral_palsy"]
            stats["mentions_dysarthria"] += record["mentions_dysarthria"]
            stats["references_removed"] += removed_references
            licenses[paper["license"]] += 1
            if record["n_replacement_chars"]:
                flagged.append({"arxiv_id": paper["arxiv_id"],
                                "n_replacement_chars": record["n_replacement_chars"]})

    summary = {"built": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
               "corpus_file": out_path.name,
               "tokenizer": f"spaCy {spacy.__version__} blank('en')",
               **stats,
               "licenses": dict(licenses.most_common()),
               "missing_markdown": missing,
               "with_replacement_chars": sorted(flagged, key=lambda f: -f["n_replacement_chars"])}
    with open(args.out_dir / f"{args.name}_stats.json", encoding="utf-8", mode="w") as fp:
        json.dump(summary, fp, indent=3)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("licenses", "with_replacement_chars")}, indent=1))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
