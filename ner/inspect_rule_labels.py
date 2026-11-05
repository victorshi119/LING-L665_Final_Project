#!/usr/bin/env python
"""
Sample rule-generated entities from the training DocBin for manual inspection.

Per label: the most frequent surface forms (where one bad pattern does the most damage)
and a random sample of mentions in context. The CSV has an empty ``verdict`` column for
the reviewer (ok / wrong_label / wrong_span / not_entity).

Outputs: inspection/rule_sample.csv, inspection/rule_surface_forms.md
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

import spacy
from spacy.tokens import DocBin

HERE = Path(__file__).resolve().parent


def context(doc, start: int, end: int, width: int = 12) -> str:
    left = doc[max(0, start - width):start].text
    right = doc[end:end + width].text
    return " ".join(f"{left} **{doc[start:end].text}** {right}".split())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--docbin", type=Path, default=HERE / "corpus" / "train.spacy")
    parser.add_argument("--per-label", type=int, default=20, help="random mentions sampled per label")
    parser.add_argument("--top-forms", type=int, default=15, help="most frequent surface forms listed per label")
    parser.add_argument("--seed", type=int, default=665)
    parser.add_argument("--output-dir", type=Path, default=HERE / "inspection")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    docs = list(DocBin().from_disk(args.docbin).get_docs(spacy.blank("en").vocab))
    mentions = defaultdict(list)          # label -> [(doc index, start, end)]
    forms = defaultdict(Counter)          # label -> surface form -> count
    form_docs = defaultdict(set)          # (label, form) -> doc ids
    for i, doc in enumerate(docs):
        for ent in doc.ents:
            mentions[ent.label_].append((i, ent.start, ent.end))
            forms[ent.label_][ent.text] += 1
            form_docs[(ent.label_, ent.text)].add(doc.user_data["doc_id"])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "rule_sample.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["label", "concept_id", "text", "doc_id", "context", "verdict", "note"])
        for label in sorted(mentions):
            for i, start, end in sorted(rng.sample(mentions[label], min(args.per_label, len(mentions[label])))):
                doc = docs[i]
                span = doc[start:end]
                writer.writerow([label, span.ent_id_ if span.ents else "", span.text,
                                 doc.user_data["doc_id"], context(doc, start, end), "", ""])

    lines = [f"# Most frequent rule-labelled surface forms ({args.docbin.name})", ""]
    for label in sorted(forms):
        total = sum(forms[label].values())
        lines += [f"## {label} ({total} mentions, {len(forms[label])} forms)", "",
                  "| form | mentions | documents |", "| --- | ---: | ---: |"]
        for text, n in forms[label].most_common(args.top_forms):
            lines.append(f"| {text} | {n} | {len(form_docs[(label, text)])} |")
        lines.append("")
    (args.output_dir / "rule_surface_forms.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"{sum(len(m) for m in mentions.values())} mentions in {len(docs)} docs; "
          f"wrote {args.output_dir}/rule_sample.csv and rule_surface_forms.md")


if __name__ == "__main__":
    main()
