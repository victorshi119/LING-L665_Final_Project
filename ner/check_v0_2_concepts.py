#!/usr/bin/env python
"""
Count how the rules and the model label the surface forms changed in glossary v0.2
(CER / PER, the removed severity terms, CAPE-V / GRBAS), per split, over all 378 documents.

Output: evaluation/v0_2_concepts.json
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import spacy
from spacy.tokens import DocBin

HERE = Path(__file__).resolve().parent
CHANGED = re.compile(r"^(PER|CER|phonemes? error rates?|phones? error rates?|character error rates?|GRBAS|"
                     r"GRBAS scale|CAPE-V|Consensus Auditory-Perceptual Evaluation of Voice)$", re.I)


def main() -> None:
    vocab = spacy.blank("en").vocab
    rules, split_of = {}, {}
    for split in ("train", "dev", "test"):
        for doc in DocBin().from_disk(HERE / "corpus" / f"{split}.spacy").get_docs(vocab):
            rules[doc.user_data["doc_id"]] = doc
            split_of[doc.user_data["doc_id"]] = split
    pred = {doc.user_data["doc_id"]: doc
            for doc in DocBin().from_disk(HERE / "corpus" / "predictions.spacy").get_docs(vocab)}

    result = {}
    for name, docs in (("rules", rules), ("model", pred)):
        changed, severity = Counter(), Counter()
        for doc_id, doc in docs.items():
            for ent in doc.ents:
                key = f"{split_of[doc_id]}\t{ent.text}\t{ent.label_}"
                if CHANGED.match(ent.text):
                    changed[key] += 1
                if "severity" in ent.text.lower():
                    severity[key] += 1
        result[name] = {"changed_forms": dict(sorted(changed.items())), "spans_with_severity": dict(severity.most_common())}

    # Spans the rules label PER in capitals: the case the long-form guard does not catch
    # ("BEST PERFORMANCE PER LANGUAGE" in a paper that also writes "phoneme error rate").
    caps_per = []
    for doc_id, doc in rules.items():
        for ent in doc.ents:
            if ent.text == "PER":
                left = doc[max(0, ent.start - 4):ent.start].text
                right = doc[ent.end:ent.end + 3].text
                if left.isupper() or right.isupper():
                    caps_per.append({"doc_id": doc_id, "split": split_of[doc_id], "context": f"{left} [PER] {right}",
                                     "model_labels_it": any(e.start == ent.start and e.end == ent.end
                                                            for e in pred[doc_id].ents)})
    result["rules_PER_in_capitals"] = caps_per

    (HERE / "evaluation" / "v0_2_concepts.json").write_text(json.dumps(result, indent=1, ensure_ascii=False))
    print(json.dumps(result, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
