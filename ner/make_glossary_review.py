#!/usr/bin/env python
"""
Write a review sheet with one row per glossary concept, so the team can check
that every term belongs to its label (the six labels themselves are fixed).

Columns: label, id, preferred term, alternate terms, acronyms, definition, corpus
mentions and documents (from glossary_stats.csv), a ``flag`` for borderline
assignments, and empty ``verdict`` / ``note`` columns for the reviewer
(ok / move:<LABEL> / remove / narrow).

Outputs: inspection/glossary_review.csv, and inspection/glossary_review.md (the same
concepts grouped by label, for reading on GitHub)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Borderline label assignments worth a deliberate decision.
FLAGS = {
    "ASM009": "ASSESSMENT is defined as a *named* instrument; perceptual evaluation is a general method",
    "TEC023": "means automatic classification, but 'severity classification' can be a clinician's rating (ASSESSMENT)",
    "TEC022": "a human listener rating used to evaluate synthesis; SPEECH_TECH or ASSESSMENT?",
    "DIS021": "voice disorder as DISORDER, while breathiness etc. are SPEECH_FEATURE",
    "DIS024": "a clinical motor sign; DISORDER includes motor signs by definition",
    "DIS025": "a clinical motor sign; DISORDER includes motor signs by definition",
    "DIS026": "a clinical motor sign; DISORDER includes motor signs by definition",
    "SPF017": "a measurement from a standard task; SPEECH_FEATURE or ASSESSMENT?",
    "SPF018": "a measurement from a standard task; SPEECH_FEATURE or ASSESSMENT?",
    "TRT009": "not a speech treatment; TREATMENT covers the underlying motor disorder",
    "TRT010": "not a speech treatment; TREATMENT covers the underlying motor disorder",
}


def cell(text: str) -> str:
    return text.replace("|", "\\|")


def write_markdown(path: Path, rows: list[dict], labels: dict[str, str]) -> None:
    lines = ["# Glossary review by category", "",
             "One table per category. ⚑ marks a borderline assignment. Same content as "
             "[glossary_review.csv](glossary_review.csv).", ""]
    for label, description in labels.items():
        group = [r for r in rows if r["label"] == label]
        lines += [f"## {label} ({len(group)} concepts)", "", description, "",
                  "| Term | Also | Definition | Mentions | Flag |", "| --- | --- | --- | ---: | --- |"]
        for r in group:
            also = "; ".join(x for x in (r["alternate_terms"], r["acronyms"]) if x)
            flag = f"⚑ {r['flag']}" if r["flag"] else ""
            lines.append(f"| **{cell(r['preferred_term'])}** | {cell(also)} | {cell(r['definition'])} "
                         f"| {r['mentions']} | {cell(flag)} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    glossary = json.loads((HERE / "glossary.json").read_text(encoding="utf-8"))
    with (HERE / "glossary_stats.csv").open(encoding="utf-8") as file:
        stats = {row["id"]: row for row in csv.DictReader(file)}
    order = list(glossary["metadata"]["labels"])

    rows = []
    for entry in sorted(glossary["entries"], key=lambda e: (order.index(e["concept_label"]), e["id"])):
        s = stats[entry["id"]]
        rows.append({
            "label": entry["concept_label"], "id": entry["id"], "preferred_term": entry["term"][0],
            "alternate_terms": "; ".join(entry["term"][1:]), "acronyms": "; ".join(entry.get("acronym", [])),
            "definition": entry["definition"][0],
            "mentions": int(s["term_mentions"]) + int(s["acronym_mentions"]), "documents": s["documents"],
            "flag": FLAGS.get(entry["id"], ""), "verdict": "", "note": "",
        })
    out = HERE / "inspection" / "glossary_review.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_markdown(out.with_suffix(".md"), rows, glossary["metadata"]["labels"])
    print(f"Wrote {len(rows)} concepts ({sum(bool(r['flag']) for r in rows)} flagged) to {out} and .md")


if __name__ == "__main__":
    main()
