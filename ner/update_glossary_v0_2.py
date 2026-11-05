#!/usr/bin/env python
"""
Apply the team's category-check corrections to glossary v0.1 and write glossary v0.2.

Corrections found by Victor (2026-11-03):
  1. TEC003 listed phoneme/phone error rate as names of character error rate (CER). PER is a
     different metric -> new concept TEC024 with acronym PER. PER is guarded by the long form,
     because in capitalised table captions it is often the word "per" ("BEST RESULTS PER METRIC").
  2. TEC023 (automatic dysarthria detection/classification) included the generic terms
     "severity classification" and "dysarthria severity assessment", which also mean a
     clinician's rating (the human gold label) -> removed.
  3. ASM010 merged CAPE-V and GRBAS, two different perceptual voice rating instruments
     -> CAPE-V stays ASM010, GRBAS becomes ASM011. The old source (ASHA voice disorders page)
     names neither instrument, so each now cites its own source.

Input: glossary_v0.1.json   Output: glossary.json
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATE = "2026-11-03"


def main() -> None:
    glossary = json.loads((HERE / "glossary_v0.1.json").read_text(encoding="utf-8"))
    entries = {e["id"]: e for e in glossary["entries"]}

    cer = entries["TEC003"]
    cer["term"] = ["character error rate"]
    cer["definition"] = ["An error rate computed like WER but over characters instead of words; used for "
                         "languages without word spacing and for character-level evaluation."]
    per = {
        "id": "TEC024", "concept_label": "SPEECH_TECH",
        "term": ["phoneme error rate", "phone error rate"], "acronym": ["PER"],
        "acronym_requires_long_form": True,
        "definition": ["An error rate computed like WER but over phonemes (or phones) instead of words; the "
                       "standard metric for phone recognition and for pronunciation-level evaluation."],
        "hypernym": "evaluation metric",
        "source_url": ["https://doi.org/10.1109/29.46546", "https://arxiv.org/abs/2601.21205"],
        "notes": f"Split from TEC003 (CER) in v0.2 ({DATE}). Sources: Lee & Hon (1989), phone recognition "
                 "on TIMIT; a corpus paper that defines PER.",
    }

    detection = entries["TEC023"]
    detection["term"] = [t for t in detection["term"]
                         if t not in ("severity classification", "dysarthria severity assessment")]
    detection["notes"] += (f" v0.2 ({DATE}): removed 'severity classification' and 'dysarthria severity "
                           "assessment', which also mean a clinician's severity rating.")

    cape_v = entries["ASM010"]
    cape_v.update({
        "term": ["Consensus Auditory-Perceptual Evaluation of Voice"], "acronym": ["CAPE-V"],
        "definition": ["A standardized clinical protocol for auditory-perceptual voice rating: overall "
                       "severity, roughness, breathiness, strain, pitch and loudness, each on a 100-mm visual "
                       "analog scale."],
        "source_url": ["https://doi.org/10.1044/1058-0360(2008/08-0017)"],
        "notes": f"GRBAS split off as ASM011 in v0.2 ({DATE}). Source: Kempster et al. (2009).",
    })
    grbas = {
        "id": "ASM011", "concept_label": "ASSESSMENT",
        "term": ["GRBAS scale"], "acronym": ["GRBAS"],
        "definition": ["A perceptual voice rating scale that rates Grade (overall severity), Roughness, "
                       "Breathiness, Asthenia and Strain, each from 0 (normal) to 3 (severe)."],
        "hypernym": "voice assessment",
        "source_url": ["https://doi.org/10.1016/s0892-1997(99)80006-x"],
        "notes": f"Split from ASM010 in v0.2 ({DATE}). Introduced by Hirano (1981), Clinical Examination of "
                 "Voice (book, no DOI); source cited here: Wuyts et al. (1999), a reliability study of the scale.",
    }

    ordered = []
    for entry in glossary["entries"]:
        ordered.append(entry)
        if entry["id"] == "TEC023":
            ordered.append(per)
        if entry["id"] == "ASM010":
            ordered.append(grbas)
    glossary["entries"] = ordered

    meta = glossary["metadata"]
    meta["version"] = "0.2"
    meta["review_status"] = (
        "Definitions are paraphrased from the cited sources (drafted with Claude Code). v0.2: the team checked "
        f"that every term belongs in its label ({DATE}); Victor found three errors, corrected here "
        "(see changes). Source URLs re-checked with verify_glossary.py.")
    meta["changes"] = [
        f"v0.2 {DATE}: TEC003 split into CER (TEC003) and phoneme/phone error rate (new TEC024, acronym PER).",
        f"v0.2 {DATE}: TEC023 lost the ambiguous terms 'severity classification' and 'dysarthria severity "
        "assessment'.",
        f"v0.2 {DATE}: ASM010 split into CAPE-V (ASM010) and GRBAS (new ASM011), each with its own source.",
    ]
    (HERE / "glossary.json").write_text(json.dumps(glossary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"glossary v0.2: {len(ordered)} concepts")


if __name__ == "__main__":
    main()
