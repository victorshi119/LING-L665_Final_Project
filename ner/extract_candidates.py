#!/usr/bin/env python
"""
Extract candidate glossary terms from the corpus with spaCy + pytextrank, as in
the course notebook code/NLP/keywords.ipynb, and mark which candidates the
glossary already covers.

TextRank is run per document (first 100k characters); a phrase's corpus score is
the sum of its per-document ranks, and its document frequency is also reported.
The glossary was drafted from MeSH/ASHA sources and corpus term counts; this
script was run afterwards as a coverage check. Uncovered candidates are only
suggestions: verify them against reliable sources before adding any to glossary.json.

Output: candidate_terms.csv (top 500)
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import pytextrank  # noqa: F401  (registers the "textrank" pipe)
import spacy

from rules import load_glossary, make_rule_pipeline

HERE = Path(__file__).resolve().parent


def main() -> None:
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    nlp.add_pipe("textrank")
    nlp.max_length = 200_000
    rules = make_rule_pipeline(load_glossary())

    score: Counter[str] = Counter()
    docs_with: defaultdict[str, set[str]] = defaultdict(set)
    paths = sorted((HERE / "texts").glob("*.txt"))
    for i, path in enumerate(paths, 1):
        doc = nlp(path.read_text(encoding="utf-8")[:100_000])
        for phrase in doc._.phrases[:60]:
            key = " ".join(phrase.text.lower().split())
            if len(key) < 3 or key.isdigit():
                continue
            score[key] += phrase.rank
            docs_with[key].add(path.stem)
        if i % 50 == 0:
            print(f"{i}/{len(paths)} documents", flush=True)

    rows = []
    for phrase, total in score.most_common(500):
        ents = rules(phrase).ents
        covered = "full" if ents and ents[0].start == 0 and ents[-1].end == len(rules(phrase)) and len(ents) == 1 \
            else "partial" if ents else "no"
        rows.append({"phrase": phrase, "textrank_score": round(total, 4), "documents": len(docs_with[phrase]),
                     "in_glossary": covered,
                     "matched_concepts": ";".join(f"{e.ent_id_}:{e.label_}" for e in ents)})
    with (HERE / "candidate_terms.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} candidates; covered fully: {sum(r['in_glossary'] == 'full' for r in rows)}, "
          f"partially: {sum(r['in_glossary'] == 'partial' for r in rows)}")


if __name__ == "__main__":
    main()
