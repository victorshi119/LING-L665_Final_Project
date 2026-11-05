#!/usr/bin/env python
"""
Classify the spans on which the model and the rules disagree on the test split.

evaluate.py counts a span as a disagreement unless start, end and label all match.
This script separates those spans into:
  boundary   model and rule spans overlap but differ in extent (e.g. "acquired cerebral palsy"
             vs "cerebral palsy"), counted once per overlapping pair
  model_new  model span that overlaps no rule span
  rule_miss  rule span that overlaps no model span
and records how many of each are written in capitals (headings, titles, table headers).

Output: evaluation/disagreements.json (counts, frequent examples) and
        evaluation/disagreement_spans.csv (every disagreement span with its context)
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import spacy
from spacy.tokens import DocBin

HERE = Path(__file__).resolve().parent


def load(path: Path, vocab) -> dict:
    return {doc.user_data["doc_id"]: doc for doc in DocBin().from_disk(path).get_docs(vocab)}


def is_caps(span) -> bool:
    letters = [c for c in span.text if c.isalpha()]
    return len(letters) > 3 and all(c.isupper() for c in letters)


def context(span, width: int = 12) -> str:
    doc = span.doc
    left = doc[max(0, span.start - width):span.start].text
    right = doc[span.end:span.end + width].text
    return " ".join(f"{left} **{span.text}** {right}".split())


def main() -> None:
    vocab = spacy.blank("en").vocab
    gold = load(HERE / "corpus" / "test.spacy", vocab)
    pred = load(HERE / "corpus" / "predictions.spacy", vocab)

    counts, caps = Counter(), Counter()
    examples: dict[str, list[str]] = {"boundary": [], "model_new": [], "rule_miss": []}
    rows = []
    for doc_id, g in gold.items():
        p = pred[doc_id]
        g_ents = {(e.start, e.end, e.label_): e for e in g.ents}
        p_ents = {(e.start, e.end, e.label_): e for e in p.ents}
        g_only = [e for k, e in g_ents.items() if k not in p_ents]
        p_only = [e for k, e in p_ents.items() if k not in g_ents]
        overlapping_g = set()
        for pe in p_only:
            hits = [ge for ge in g_only if ge.start < pe.end and pe.start < ge.end]
            if hits:
                counts["boundary"] += 1
                overlapping_g.update((ge.start, ge.end) for ge in hits)
                examples["boundary"].append(f"model [{pe.text}] {pe.label_} / rules [{hits[0].text}] {hits[0].label_}")
                rows.append(["boundary", doc_id, pe.text, pe.label_, hits[0].text, hits[0].label_, context(pe)])
            else:
                counts["model_new"] += 1
                caps["model_new"] += is_caps(pe)
                examples["model_new"].append(f"[{pe.text}] {pe.label_}")
                rows.append(["model_new", doc_id, pe.text, pe.label_, "", "", context(pe)])
        for ge in g_only:
            if (ge.start, ge.end) not in overlapping_g:
                counts["rule_miss"] += 1
                caps["rule_miss"] += is_caps(ge)
                examples["rule_miss"].append(f"[{ge.text}] {ge.label_} ({doc_id})")
                rows.append(["rule_miss", doc_id, "", "", ge.text, ge.label_, context(ge)])

    result = {"counts": dict(counts), "in_capitals": dict(caps),
              "examples": {k: sorted(Counter(v).items(), key=lambda x: -x[1])[:25] for k, v in examples.items()}}
    (HERE / "evaluation" / "disagreements.json").write_text(json.dumps(result, indent=1, ensure_ascii=False))
    with open(HERE / "evaluation" / "disagreement_spans.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["kind", "doc_id", "model_text", "model_label", "rule_text", "rule_label", "context"])
        writer.writerows(rows)
    print(json.dumps({"counts": result["counts"], "in_capitals": result["in_capitals"]}, indent=1))
    for kind, items in result["examples"].items():
        print(f"\n{kind}:", "; ".join(f"{t} ×{n}" for t, n in items[:15]))


if __name__ == "__main__":
    main()
