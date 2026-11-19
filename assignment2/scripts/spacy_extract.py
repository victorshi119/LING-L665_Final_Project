"""spaCy extractor: default parser plus the Assignment 1 domain NER model.

Run with the course environment, which has spaCy, en_core_web_sm, and
spacy-transformers. That environment does not include en_core_web_trf, so
sentence structure comes from en_core_web_sm. Domain labels come from
model-best and are stored as spans named domain_ner. The predicate comes
from a dependency cue in the same sentence, not from either NER model.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import MODEL_DIR, PREDICATES, load_sources, read_text, write_triples

CUES = {
    "has_feature": {"exhibit", "show", "present", "characterize", "feature", "include", "display", "cause", "produce", "affect", "manifest"},
    "measures": {"measure", "assess", "rate", "quantify", "evaluate", "score"},
    "treats": {"treat", "improve", "manage", "rehabilitate", "reduce", "therapy"},
    "evaluated_on": {"train", "test", "evaluate", "corpus", "dataset", "database"},
    "applied_to": {"recognize", "detect", "classify", "identify", "diagnose", "reconstruct"},
}
MODALS = {"may", "might", "could", "would"}
MAX_SPAN = 80


def domain_spans(sentence, domain_doc) -> list[dict]:
    spans = []
    for ent in domain_doc.ents:
        if ent.label_ not in {side for pair in PREDICATES.values() for side in pair}:
            continue
        label = " ".join(ent.text.split())
        if not label or len(label) > MAX_SPAN:
            continue
        spans.append(
            {
                "label": label,
                "type": ent.label_,
                "start": sentence.start_char + ent.start_char,
                "end": sentence.start_char + ent.end_char,
            }
        )
    return spans


def sentence_flags(sentence) -> tuple[str, str]:
    lemmas = {token.lemma_.lower() for token in sentence}
    polarity = "negative" if any(token.dep_ == "neg" for token in sentence) else "positive"
    modality = next((token.lemma_.lower() for token in sentence if token.lemma_.lower() in MODALS), "")
    return polarity, modality if modality in lemmas or modality else modality


def pairs_for_sentence(sentence, spans: list[dict], doc_id: str) -> list[dict]:
    polarity, modality = sentence_flags(sentence)
    lemmas = {token.lemma_.lower() for token in sentence}
    evidence = " ".join(sentence.text.split())[:500]
    rows = []
    seen = set()
    for predicate, (subject_type, object_type) in PREDICATES.items():
        if not (lemmas & CUES[predicate]):
            continue
        subjects = [span for span in spans if span["type"] == subject_type]
        objects = [span for span in spans if span["type"] == object_type]
        for subject in subjects:
            for obj in objects:
                if subject["start"] == obj["start"]:
                    continue
                key = (predicate, subject["label"].lower(), obj["label"].lower())
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "doc_id": doc_id,
                        "extractor": "spacy",
                        "subject": subject["label"],
                        "subject_type": subject_type,
                        "predicate": predicate,
                        "object": obj["label"],
                        "object_type": object_type,
                        "polarity": polarity,
                        "modality": modality,
                        "evidence": evidence,
                        "entity_source": "domain_ner",
                    }
                )
    return rows


def main() -> None:
    import spacy

    if not (MODEL_DIR / "config.cfg").exists():
        raise SystemExit(f"Domain model not found at {MODEL_DIR}")
    parser = spacy.load("en_core_web_sm")
    domain = spacy.load(MODEL_DIR)
    rows = []
    for source in load_sources():
        doc_id = source["doc_id"]
        text = read_text(doc_id)
        parsed = parser(text)
        sentences = [sent for sent in parsed.sents if sent.text.strip()]
        domain_docs = list(domain.pipe((sent.text for sent in sentences), batch_size=32))
        doc_rows = []
        for sentence, domain_doc in zip(sentences, domain_docs):
            spans = domain_spans(sentence, domain_doc)
            if len(spans) < 2:
                continue
            doc_rows.extend(pairs_for_sentence(sentence, spans, doc_id))
        print(f"{doc_id}: {len(doc_rows)} triples", flush=True)
        rows.extend(doc_rows)
    path = write_triples("spacy", rows)
    print(f"wrote {len(rows)} triples to {path}")


if __name__ == "__main__":
    main()
