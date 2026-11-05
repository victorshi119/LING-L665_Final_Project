#!/usr/bin/env python
"""
Rule-annotate every document in texts/ and write train/dev/test DocBins.

* One spaCy Doc per source document; Doc.user_data stores doc_id, source, split,
  title, url, license, and the glossary version used for the weak labels.
* Split by document (80/10/10), stratified by source (arXiv / PubMed), with a
  fixed seed. Documents listed together in sources_raw/near_duplicates.json
  ("split_groups") are always assigned to the same split.
* Outputs: corpus/{train,dev,test}.spacy, corpus/splits.csv, corpus/corpus_stats.json
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from spacy.tokens import DocBin

from rules import load_glossary, make_rule_pipeline

HERE = Path(__file__).resolve().parent
SPLITS = ("train", "dev", "test")
ATTRS = ["ORTH", "SPACY", "ENT_IOB", "ENT_TYPE", "ENT_ID", "SENT_START"]


def group_documents(doc_ids: list[str], groups: list[list[str]]) -> dict[str, str]:
    """Union-find: map every document to a representative of its near-duplicate group."""
    parent = {doc_id: doc_id for doc_id in doc_ids}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for group in groups:
        present = [d for d in group if d in parent]
        for other in present[1:]:
            parent[find(other)] = find(present[0])
    return {doc_id: find(doc_id) for doc_id in doc_ids}


def assign_splits(rows: list[dict], groups: dict[str, str], seed: int) -> dict[str, str]:
    rng = random.Random(seed)
    assignment: dict[str, str] = {}
    for source in sorted({row["source"] for row in rows}):
        units = sorted({groups[row["doc_id"]] for row in rows if row["source"] == source})
        rng.shuffle(units)
        n_dev = max(1, round(len(units) * 0.10))
        n_test = max(1, round(len(units) * 0.10))
        for i, unit in enumerate(units):
            assignment[unit] = "dev" if i < n_dev else "test" if i < n_dev + n_test else "train"
    return {row["doc_id"]: assignment[groups[row["doc_id"]]] for row in rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=665)
    parser.add_argument("--output-dir", type=Path, default=HERE / "corpus")
    args = parser.parse_args()

    glossary = load_glossary()
    nlp = make_rule_pipeline(glossary)
    nlp.max_length = 2_000_000

    with (HERE / "sources.csv").open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    split_groups = json.loads((HERE / "sources_raw" / "near_duplicates.json").read_text())["split_groups"]
    groups = group_documents([row["doc_id"] for row in rows], split_groups)
    split_of = assign_splits(rows, groups, args.seed)

    bins = {split: DocBin(attrs=ATTRS, store_user_data=True) for split in SPLITS}
    records = []
    stats = {split: {"documents": 0, "tokens": 0, "entities": Counter(), "concepts": set()} for split in SPLITS}
    texts = ((HERE / row["text_file"]).read_text(encoding="utf-8") for row in rows)
    for row, doc in zip(rows, nlp.pipe(texts, batch_size=8)):
        split = split_of[row["doc_id"]]
        doc.user_data.update({
            "doc_id": row["doc_id"], "source": row["source"], "split": split, "title": row["title"],
            "url": row["url"], "license": row["license"], "annotation": "rule-based (weak labels)",
            "glossary_version": glossary["metadata"]["version"],
        })
        bins[split].add(doc)
        labels = Counter(ent.label_ for ent in doc.ents)
        stats[split]["documents"] += 1
        stats[split]["tokens"] += len(doc)
        stats[split]["entities"].update(labels)
        stats[split]["concepts"].update(ent.ent_id_ for ent in doc.ents)
        records.append({
            "doc_id": row["doc_id"], "source": row["source"], "split": split,
            "split_group": groups[row["doc_id"]] if groups[row["doc_id"]] != row["doc_id"] else "",
            "n_tokens": len(doc), "n_sentences": sum(1 for _ in doc.sents), "n_entities": len(doc.ents),
            **{f"n_{label}": labels.get(label, 0) for label in glossary["metadata"]["labels"]},
            "text_file": row["text_file"],
        })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for split in SPLITS:
        bins[split].to_disk(args.output_dir / f"{split}.spacy")
    with (args.output_dir / "splits.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    summary = {
        "seed": args.seed,
        "glossary_version": glossary["metadata"]["version"],
        "docbin_attrs": ATTRS,
        "splits": {
            split: {
                "documents": s["documents"], "tokens": s["tokens"],
                "entities": sum(s["entities"].values()), "entities_per_label": dict(sorted(s["entities"].items())),
                "distinct_concepts": len(s["concepts"]),
            } for split, s in stats.items()
        },
    }
    (args.output_dir / "corpus_stats.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
