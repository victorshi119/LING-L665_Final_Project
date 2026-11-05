# Assignment 1: Domain Glossary and Transformer NER

CP-associated dysarthria. The labels are described in [topic_and_labels.md](topic_and_labels.md),
and the glossary is [glossary.json](glossary.json). This folder is a copy of `ner_assignment1/`
on Quartz.

Not in this repo:

| What | Why | Where |
| --- | --- | --- |
| `texts/` (378 documents) and the DocBins (`corpus/*.spacy`, including `predictions.spacy`) | many papers' licenses do not allow redistribution (see `sources.csv`) | Quartz: `/N/u/shinsaka/BigRed200/CP_Dysarthria_Pubmed_md/ner_assignment1/` |
| trained models (`training/*/model-best/`, `model-last/`, 484 MB each) | too large for GitHub | same folder |
| `build_ner_corpus.py`, `train_transformer_ner.py` | course material (dcavar/L665, all rights reserved) | copy from the course repo (`code/NER`); `rules.py` imports `build_ner_corpus.py` |
