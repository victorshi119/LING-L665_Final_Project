#!/usr/bin/env python
"""
Turn glossary.json into a spaCy rule-based NER pipeline.

Built on the course script build_ner_corpus.py (copied unchanged from the L665
repository, code/NER), whose singular/plural expansion is reused. Differences:

* every pattern carries the glossary concept id (e.g. TEC001) as its EntityRuler
  ``id``, so all alternate names and acronyms of a concept map to one ``ent_id_``;
* terms match case-insensitively (LOWER phrase patterns), while acronyms are
  token patterns on ORTH, so they match with exact case only ("CP", not "cp");
* acronyms flagged ``acronym_requires_long_form`` are removed from a document in
  which none of the concept's terms occur (e.g. "FDA" is kept only in documents
  that also mention "Frenchay Dysarthria Assessment");
* documents get sentence boundaries (punctuation and blank lines), stored in the
  DocBins so that spaCy training can split long papers into sentences.

Usage:
    from rules import load_glossary, build_patterns, make_rule_pipeline
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import spacy
from spacy.language import Language
from spacy.tokens import Doc

from build_ner_corpus import singular_plural_variants

HERE = Path(__file__).resolve().parent
GLOSSARY = HERE / "glossary.json"


def load_glossary(path: str | Path = GLOSSARY) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as file:
        return json.load(file)


def term_variants(term: str) -> set[str]:
    """Singular/plural forms plus a hyphen/space alternation (self-supervised ~ self supervised)."""
    forms = singular_plural_variants(term)
    for form in list(forms):
        if "-" in form:
            forms.add(form.replace("-", " "))
    return forms


def build_patterns(glossary: dict[str, Any], nlp: Language) -> tuple[list[dict], dict[str, set[str]]]:
    """Return EntityRuler patterns and, per concept id, the acronym forms that need a long form."""
    patterns: list[dict] = []
    owners: dict[str, str] = {}
    guarded_acronyms: dict[str, set[str]] = defaultdict(set)

    def claim(key: str, concept_id: str) -> bool:
        previous = owners.setdefault(key, concept_id)
        if previous != concept_id:
            raise ValueError(f"Surface form {key!r} is used by {previous} and {concept_id}")
        return True

    for entry in glossary["entries"]:
        label, concept_id = entry["concept_label"], entry["id"]
        terms = set().union(*(term_variants(term) for term in entry["term"]))
        for form in sorted(terms):
            claim(form.casefold(), concept_id)
            patterns.append({"label": label, "pattern": form, "id": concept_id})
        for acronym in entry.get("acronym", []):
            for form in sorted(singular_plural_variants(acronym, acronym=True)):
                claim(form, concept_id)
                tokens = [{"ORTH": token.text} for token in nlp.make_doc(form)]
                patterns.append({"label": label, "pattern": tokens, "id": concept_id})
                if entry.get("acronym_requires_long_form"):
                    guarded_acronyms[concept_id].add(form)
    return patterns, guarded_acronyms


@Language.component("paragraph_sentences")
def paragraph_sentences(doc: Doc) -> Doc:
    """Also start a sentence after every line break (headings, table rows, list items)."""
    for token in doc[1:]:
        if doc[token.i - 1].is_space and "\n" in doc[token.i - 1].text:
            token.is_sent_start = True
    return doc


def make_rule_pipeline(glossary: dict[str, Any] | None = None) -> Language:
    glossary = glossary or load_glossary()
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    nlp.add_pipe("paragraph_sentences")
    patterns, guarded = build_patterns(glossary, nlp)
    ruler = nlp.add_pipe(
        "entity_ruler",
        config={"phrase_matcher_attr": "LOWER", "validate": True, "overwrite_ents": True},
    )
    ruler.add_patterns(patterns)
    nlp.add_pipe("long_form_filter", config={"guarded": {k: sorted(v) for k, v in guarded.items()}})
    nlp.meta["name"] = "cp_dysarthria_rules"
    nlp.meta["version"] = glossary["metadata"]["version"]
    return nlp


@Language.factory("long_form_filter", default_config={"guarded": {}})
def make_long_form_filter(nlp: Language, name: str, guarded: dict[str, list[str]]):
    guarded_sets = {concept: set(forms) for concept, forms in guarded.items()}

    def long_form_filter(doc: Doc) -> Doc:
        # A concept counts as "introduced" when one of its non-acronym forms matched.
        introduced = {
            ent.ent_id_ for ent in doc.ents
            if not (ent.ent_id_ in guarded_sets and ent.text in guarded_sets[ent.ent_id_])
        }
        doc.ents = [
            ent for ent in doc.ents
            if not (ent.ent_id_ in guarded_sets and ent.text in guarded_sets[ent.ent_id_]
                    and ent.ent_id_ not in introduced)
        ]
        return doc

    return long_form_filter


if __name__ == "__main__":
    glossary = load_glossary()
    nlp = make_rule_pipeline(glossary)
    patterns, guarded = build_patterns(glossary, nlp)
    print(f"{len(glossary['entries'])} concepts -> {len(patterns)} EntityRuler patterns")
    print(f"{sum(len(v) for v in guarded.values())} acronym forms require a long form: "
          + ", ".join(sorted(f for forms in guarded.values() for f in forms)))
    print("Pipeline:", nlp.pipe_names)
