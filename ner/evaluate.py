#!/usr/bin/env python
"""
Compare model predictions with the rule-generated (weak) labels on the held-out
test documents, and collect examples for manual inspection.

Reads corpus/test.spacy (rule labels) and corpus/predictions.spacy (model).
Writes evaluation/:
  scores.json              precision/recall/F1 overall and per label, vs. rule labels
  confusion.json           label agreement on exactly matching spans
  model_only_terms.csv     spans the model tagged but the rules did not (candidate new terms)
  rule_only_terms.csv      spans the rules tagged but the model missed
  examples.md              sampled agreements, model-only, rule-only, and label conflicts in context
"""

from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import spacy
from spacy.scorer import Scorer
from spacy.tokens import DocBin
from spacy.training import Example

HERE = Path(__file__).resolve().parent
OUT = HERE / "evaluation"


def load(path: Path, vocab) -> dict[str, object]:
    return {doc.user_data["doc_id"]: doc for doc in DocBin().from_disk(path).get_docs(vocab)}


def context(doc, start: int, end: int, width: int = 12) -> str:
    left = doc[max(0, start - width):start].text
    right = doc[end:end + width].text
    return " ".join(f"{left} **{doc[start:end].text}** {right}".split())


def main() -> None:
    random.seed(665)
    vocab = spacy.blank("en").vocab
    gold = load(HERE / "corpus" / "test.spacy", vocab)
    pred = load(HERE / "corpus" / "predictions.spacy", vocab)
    missing = sorted(set(gold) - set(pred))
    if missing:
        raise ValueError(f"No predictions for test documents: {missing[:5]} ...")

    examples = []
    model_only, rule_only = Counter(), Counter()
    model_only_ctx, rule_only_ctx = defaultdict(list), defaultdict(list)
    agree, conflicts = [], []
    confusion = Counter()
    for doc_id, g in gold.items():
        p = pred[doc_id]
        assert [t.text for t in g] == [t.text for t in p], f"tokenization differs for {doc_id}"
        examples.append(Example(p, g))
        g_spans = {(e.start, e.end): e.label_ for e in g.ents}
        p_spans = {(e.start, e.end): e.label_ for e in p.ents}
        for span, label in p_spans.items():
            if span in g_spans:
                confusion[(g_spans[span], label)] += 1
                item = (doc_id, label, g_spans[span], context(g, *span))
                (agree if label == g_spans[span] else conflicts).append(item)
            else:
                key = (p[span[0]:span[1]].text.lower(), label)
                model_only[key] += 1
                model_only_ctx[key].append((doc_id, context(p, *span)))
        for span, label in g_spans.items():
            if span not in p_spans:
                key = (g[span[0]:span[1]].text.lower(), label)
                rule_only[key] += 1
                rule_only_ctx[key].append((doc_id, context(g, *span)))

    scores = Scorer.score_spans(examples, "ents")
    result = {
        "test_documents": len(examples),
        "reference": "rule-generated weak labels (not human gold)",
        "rule_entities": sum(len(g.ents) for g in gold.values()),
        "predicted_entities": sum(len(pred[d].ents) for d in gold),
        "ents_p": scores["ents_p"], "ents_r": scores["ents_r"], "ents_f": scores["ents_f"],
        "ents_per_type": scores["ents_per_type"],
        "exact_span_label_conflicts": len(conflicts),
        "model_only_spans": sum(model_only.values()), "model_only_distinct": len(model_only),
        "rule_only_spans": sum(rule_only.values()), "rule_only_distinct": len(rule_only),
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "scores.json").write_text(json.dumps(result, indent=1))
    (OUT / "confusion.json").write_text(json.dumps(
        {f"{g} -> {p}": n for (g, p), n in sorted(confusion.items())}, indent=1))

    for name, counter, ctx in (("model_only_terms.csv", model_only, model_only_ctx),
                               ("rule_only_terms.csv", rule_only, rule_only_ctx)):
        with (OUT / name).open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["text", "label", "count", "documents", "example_doc", "example_context"])
            for (text, label), n in counter.most_common():
                docs = {d for d, _ in ctx[(text, label)]}
                writer.writerow([text, label, n, len(docs), *ctx[(text, label)][0]])

    def sample(items, k):
        return random.sample(items, min(k, len(items)))

    lines = ["# Inspected examples (test split)", "",
             "Reference = rule-generated weak labels. Contexts are 12 tokens either side; the entity is in bold.", ""]
    lines += ["## Agreements (model = rules)", ""]
    lines += [f"- `{d}` {lab}: {c}" for d, lab, _, c in sample(agree, 15)]
    lines += ["", "## Label conflicts (same span, different label)", ""]
    lines += [f"- `{d}` rules={g} model={p}: {c}" for d, p, g, c in sample(conflicts, 15)] or ["- none"]
    lines += ["", "## Model-only spans (most frequent; candidate glossary additions or model errors)", ""]
    for (text, label), n in model_only.most_common(40):
        d, c = model_only_ctx[(text, label)][0]
        lines.append(f"- **{text}** → {label} ×{n} — `{d}`: {c}")
    lines += ["", "## Rule-only spans (most frequent; missed by the model)", ""]
    for (text, label), n in rule_only.most_common(25):
        d, c = rule_only_ctx[(text, label)][0]
        lines.append(f"- **{text}** ({label}) ×{n} — `{d}`: {c}")
    (OUT / "examples.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "ents_per_type"}, indent=1))
    for label, s in sorted(result["ents_per_type"].items()):
        print(f"{label:15} P={s['p']:.3f} R={s['r']:.3f} F={s['f']:.3f}")


if __name__ == "__main__":
    main()
