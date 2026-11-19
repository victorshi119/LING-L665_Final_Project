#!/usr/bin/env python
"""
Measure text shared between the training split and the dev/test splits.

`spacy debug data` warns when training sentences also occur in the evaluation data.
Most such sentences are headings, numbers, or licence boilerplate; this script counts
only sentences with at least --min-words words and reports, for each (dev/test document,
training document) pair, how many sentences they share and what fraction of the
dev/test document's sentences that is.

Output: inspection/split_overlap.csv
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

import spacy
from spacy.tokens import DocBin

HERE = Path(__file__).resolve().parent


def sentences(path: Path, vocab, min_words: int) -> dict[str, set[str]]:
    """doc_id -> set of normalised sentences with at least min_words words."""
    out: dict[str, set[str]] = {}
    for doc in DocBin().from_disk(path).get_docs(vocab):
        out[doc.user_data["doc_id"]] = {
            " ".join(s.text.split()) for s in doc.sents if len(s.text.split()) >= min_words
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--min-words", type=int, default=8)
    parser.add_argument("--output", type=Path, default=HERE / "inspection" / "split_overlap.csv")
    args = parser.parse_args()

    vocab = spacy.blank("en").vocab
    train = sentences(HERE / "corpus" / "train.spacy", vocab, args.min_words)
    owners: dict[str, set[str]] = defaultdict(set)
    for doc_id, sents in train.items():
        for sent in sents:
            owners[sent].add(doc_id)

    rows = []
    for split in ("dev", "test"):
        for doc_id, sents in sentences(HERE / "corpus" / f"{split}.spacy", vocab, args.min_words).items():
            shared = Counter(owner for sent in sents for owner in owners.get(sent, ()))
            for train_id, n in shared.items():
                rows.append({"split": split, "doc_id": doc_id, "train_doc_id": train_id, "shared_sentences": n,
                             "doc_sentences": len(sents), "fraction_of_doc": round(n / len(sents), 4)})
    rows.sort(key=lambda r: -r["fraction_of_doc"])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["split", "doc_id", "train_doc_id", "shared_sentences",
                                                  "doc_sentences", "fraction_of_doc"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} (dev/test doc, train doc) pairs share >= {args.min_words}-word sentences")
    for r in rows[:20]:
        print(f"{r['split']:4} {r['doc_id']:20} ~ {r['train_doc_id']:20} "
              f"{r['shared_sentences']:4}/{r['doc_sentences']:<5} ({r['fraction_of_doc']:.1%})")


if __name__ == "__main__":
    main()
