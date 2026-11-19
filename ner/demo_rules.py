#!/usr/bin/env python
"""
Demonstrate the glossary rules on short passages and record what they get wrong.

Writes rules_demo.md (bracketed entities, per passage) and rules_demo.html
(displaCy rendering of the same passages).
"""

from __future__ import annotations

import re
from pathlib import Path

from spacy import displacy

from rules import load_glossary, make_rule_pipeline

HERE = Path(__file__).resolve().parent

# Real passages: the first paragraph with >= 4 rule entities in each document.
CORPUS_DOCS = [
    "pubmed_34942852",   # consonantal landmarks, adults with CP
    "pubmed_36892950",   # intelligibility cut-points, children with CP
    "pubmed_35262181",   # Viking Speech Scale, children with CP
    "arxiv_2204.00770",  # speaker adaptation for wav2vec2 dysarthric ASR
    "pubmed_40409971",   # dysarthria outcome measures after stroke
]

# Constructed sentences that probe specific rule behaviour.
PROBES = [
    ("Acronym needs its long form: FDA kept",
     "Speech was rated with the Frenchay Dysarthria Assessment (FDA); FDA scores correlated with intelligibility."),
    ("Acronym needs its long form: FDA dropped",
     "Riluzole is approved by the FDA for ALS and slows disease progression."),
    ("Acronym needs its long form: SGD dropped",
     "The Conformer model was optimised with SGD and evaluated by WER on TORGO."),
    ("Case-sensitive acronyms",
     "Children with CP were recorded; the cp command copied the files, and als was a typo."),
    ("Plurals and alternate names map to one concept id",
     "MFCCs and mel-frequency cepstral coefficients were compared with log-mel spectrograms and wav2vec2 features."),
    ("Known miss: term not in glossary",
     "Velopharyngeal dysfunction and nasal emission were frequent, and the speakers used eye-gaze systems."),
    ("Known false match: everyday sense",
     "The articulation of this argument is weak, and a single stroke of the pen changed the result."),
    ("Known boundary issue: modifier outside the span",
     "Severe spastic dysarthria and moderate hypokinetic dysarthria were compared using the GMFCS level."),
]


def bracket(doc) -> str:
    out, last = [], 0
    for ent in doc.ents:
        out.append(doc.text[last:ent.start_char])
        out.append(f"[{ent.text}]({ent.label_}:{ent.ent_id_})")
        last = ent.end_char
    out.append(doc.text[last:])
    return "".join(out)


def first_dense_paragraph(nlp, text: str, minimum: int = 4) -> str:
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = " ".join(paragraph.split())
        if 200 < len(paragraph) < 1200 and len(nlp(paragraph).ents) >= minimum:
            return paragraph
    return " ".join(text.split())[:800]


def main() -> None:
    glossary = load_glossary()
    nlp = make_rule_pipeline(glossary)
    lines = ["# Rule demonstration", "",
             f"Glossary v{glossary['metadata']['version']}: {len(glossary['entries'])} concepts. "
             "Entities are shown as `[text](LABEL:concept_id)`.", ""]
    docs_for_html = []

    lines += ["## Corpus passages", ""]
    for doc_id in CORPUS_DOCS:
        text = (HERE / "texts" / f"{doc_id}.txt").read_text(encoding="utf-8")
        doc = nlp(first_dense_paragraph(nlp, text))
        doc.user_data["title"] = doc_id
        docs_for_html.append(doc)
        lines += [f"### {doc_id}", "", bracket(doc), "",
                  "Entities: " + ", ".join(f"{e.text} ({e.label_})" for e in doc.ents), ""]

    lines += ["## Probe sentences", ""]
    for title, sentence in PROBES:
        doc = nlp(sentence)
        doc.user_data["title"] = title
        docs_for_html.append(doc)
        lines += [f"### {title}", "", bracket(doc), ""]

    (HERE / "rules_demo.md").write_text("\n".join(lines), encoding="utf-8")
    colors = {"DISORDER": "#f4a6a6", "SPEECH_FEATURE": "#a6d8f4", "ASSESSMENT": "#f4e1a6",
              "TREATMENT": "#b8f4a6", "SPEECH_TECH": "#d7b8f4", "DATASET": "#f4c6a6"}
    html = displacy.render(docs_for_html, style="ent", page=True, options={"colors": colors})
    (HERE / "rules_demo.html").write_text(html, encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
