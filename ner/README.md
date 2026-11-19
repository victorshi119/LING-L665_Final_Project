# Assignment 1: Domain Glossary and Transformer NER

CP-associated dysarthria. This folder is a copy of `ner_assignment1/` on Quartz.

## Deliverables

| # | Deliverable | File(s) | In this repo |
| --- | --- | --- | --- |
| 1 | Topic and labels | [topic_and_labels.md](topic_and_labels.md) | yes |
| 2 | Glossary | [glossary.json](glossary.json) | yes |
| 3 | Rules and demo | [rules.py](rules.py), [demo_rules.py](demo_rules.py), [rules_demo.md](rules_demo.md) | yes |
| 4 | Corpus | `texts/` (378 files), [sources.csv](sources.csv) | `sources.csv` only |
| 5 | Train/dev/test DocBins | `corpus/train.spacy`, `corpus/dev.spacy`, `corpus/test.spacy`, [corpus/splits.csv](corpus/splits.csv) | `splits.csv` only |
| 6 | Model, config, logs | `training/ner-transformer/model-best/` (484 MB), [training/config.cfg](training/config.cfg), [training/ner-transformer/train.log](training/ner-transformer/train.log) | config and log only |
| 7 | Prediction DocBin | `corpus/predictions.spacy` | no |
| 8 | Report | `report.md` | no |

The files not in this repo are on Quartz in
`/N/u/shinsaka/BigRed200/CP_Dysarthria_Pubmed_md/ner_assignment1/`:

- the texts and DocBins, because many papers' licenses do not allow redistribution (see `sources.csv`);
- the model, because it is too large for GitHub;
- the report, which is submitted separately;
- `build_ner_corpus.py` and `train_transformer_ner.py`, which are course material (dcavar/L665,
  all rights reserved). Copy them from the course repo (`code/NER`); `rules.py` imports
  `build_ner_corpus.py`.

Everything else in this folder is supporting material: the other scripts, `evaluation/`,
`inspection/`, logs, and the `_v0.1` backups of the first glossary version.
