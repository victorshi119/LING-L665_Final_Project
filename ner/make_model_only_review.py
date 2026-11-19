#!/usr/bin/env python
"""
Judge each model-only span type on the test split (spans the model predicts and the rules do not).

Judgments are a first pass by Claude Code from the contexts in evaluation/examples.md and
evaluation/disagreement_spans.csv:
  correct   a right entity the rules missed (not in the glossary, a variant, a guarded acronym)
  partial   right label, wrong boundary
  error     not an entity of that label
  boundary  overlaps a rule span with a different extent (see evaluation/disagreements.json)
Judgments for the v0.1 model (evaluation_v0.1/model_only_review.csv) are reused where the same
text and label recur; NEW holds the judgments for span types that are new with the v0.2 model.

Input:  evaluation/model_only_terms.csv, evaluation/disagreements.json
Output: evaluation/model_only_review.csv (one row per text and label, with the span count)
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

NEW = {
    ("mltcs", "SPEECH_TECH"): ("error", "multiple long-term conditions (a comorbidity paper), not speech technology"),
    ("ltcs", "SPEECH_TECH"): ("error", "long-term conditions, not speech technology"),
    ("thria", "DISORDER"): ("error", "fragment of 'dysar- thria' split by a line-end hyphen"),
    ("ters", "SPEECH_TECH"): ("error", "fragment of 'cen- ters' split by a line-end hyphen"),
    ("ers", "SPEECH_TECH"): ("error", "fragment of 'speak- ers' split by a line-end hyphen"),
    ("pc -", "DATASET"): ("partial", "part of the dataset name LibriSpeech-PC; span misses 'LibriSpeech' and includes '-'"),
    ("pc)", "DATASET"): ("partial", "part of the dataset name LibriSpeech-PC; span includes ')'"),
    ("pc", "SPEECH_TECH"): ("error", "part of the dataset name LibriSpeech-PC, labelled SPEECH_TECH"),
    ("hypernasal speakers", "SPEECH_FEATURE"): ("error", "speakers, not a speech feature"),
    ("sgd", "TREATMENT"): ("error", "stochastic gradient descent labelled TREATMENT"),
    ("informer", "SPEECH_TECH"): ("error", "a time-series forecasting model (time-series paper), not speech technology"),
    ("lm", "SPEECH_TECH"): ("correct", "language model in ASR decoding (CTC-LM); not in the glossary"),
    ("cerebral vascular", "DISORDER"): ("partial", "right label, span misses 'Accident'"),
    ("motor-speech disorders", "DISORDER"): ("correct", "motor speech disorders; not in the glossary"),
    ("universal access speech", "DATASET"): ("correct", "long name of UASpeech"),
    ("speaker level adaptation", "SPEECH_TECH"): ("correct", "speaker adaptation (in a capitalised caption); not in the glossary"),
    ("v-vectors", "SPEECH_TECH"): ("error", "vectors of a Householder transformation, not a speaker embedding like x-vectors"),
    ("c", "SPEECH_TECH"): ("error", "a hyperparameter name ('different C values')"),
    ("tc", "SPEECH_TECH"): ("error", "temporal convolution layer, a generic network component"),
    ("frequency cepstral coefficients", "SPEECH_TECH"): ("partial", "GammaTone frequency cepstral coefficients; span misses 'GammaTone'"),
    ("mel-spectrogrambased", "SPEECH_TECH"): ("partial", "'mel-spectrogram-based' glued in the source; span includes 'based'"),
    ("bert", "SPEECH_TECH"): ("error", "a text model, here naming a text-similarity score"),
    ("updrsspeech", "ASSESSMENT"): ("correct", "UPDRS speech item (glued in the source)"),
    ("speaking-", "SPEECH_FEATURE"): ("partial", "speaking rate split by a line-end hyphen; span misses 'rate'"),
    ("monoprosody", "SPEECH_FEATURE"): ("correct", "speech feature; not in the glossary"),
    ("motor neuron impairment", "DISORDER"): ("partial", "lower motor neuron impairment, a cause of flaccid dysarthria; span misses 'lower'"),
}


def main() -> None:
    old = {(r["text"], r["label"]): (r["judgment"], r["reason"])
           for r in csv.DictReader(open(HERE / "evaluation_v0.1" / "model_only_review.csv", encoding="utf-8"))
           if r["judgment"] != "boundary"}
    disagreements = json.loads((HERE / "evaluation" / "disagreements.json").read_text(encoding="utf-8"))
    boundary = set()
    for example, _ in disagreements["examples"]["boundary"]:
        m = re.match(r"model \[(.*?)\] (\S+) / rules", example)
        boundary.add((m.group(1).lower(), m.group(2)))

    rows, totals, missing = [], Counter(), []
    for r in csv.DictReader(open(HERE / "evaluation" / "model_only_terms.csv", encoding="utf-8")):
        key = (r["text"], r["label"])
        if key in boundary:
            judgment = ("boundary", "overlaps a rule span with a different extent (see disagreements.json)")
        else:
            judgment = NEW.get(key) or old.get(key)
        if judgment is None:
            missing.append(key)
            continue
        rows.append([r["text"], r["label"], r["count"], r["example_doc"], *judgment])
        totals[judgment[0]] += int(r["count"])
    if missing:
        raise SystemExit(f"no judgment for {missing}")

    with open(HERE / "evaluation" / "model_only_review.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label", "count", "example_doc", "judgment", "reason"])
        writer.writerows(rows)
    print(f"{len(rows)} span types, {sum(totals.values())} spans:", dict(totals))


if __name__ == "__main__":
    main()
