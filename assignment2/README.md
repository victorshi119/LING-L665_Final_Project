# Assignment 2: corpus to knowledge graph

Team: Victor Shi, Shintaro Sakai, and Zhanerke Asset, L665 (Fall 2026).

Instructions: [Assignment 2](https://github.com/dcavar/L665/blob/main/doc/Assignment%202%20-%20Corpus-to-Knowledge-Graph%20Assignment.md). The same file is on Quartz at `/N/project/ontology_learning/L665/L665/doc/Assignment 2 - Corpus-to-Knowledge-Graph Assignment.md`.

This folder is the code and the write-up. It does not contain the trained NER weights or the paper texts. Those stay off GitHub for the same reasons as Assignment 1: the model is about 480 MB, and many papers cannot be redistributed. Teammates rebuild the same graphs from the paths below.

## What is not in this repo

| Needed file | Where it is | Why it is not committed |
|---|---|---|
| Trained NER model | `/N/project/CoRSAL/L665_Assignment2_work/model-best` and `/N/project/CoRSAL/L665_Assignment1_submit/model-best.zip` | Too large for GitHub. Shintaro's copy on Quartz is `/N/u/shinsaka/BigRed200/CP_Dysarthria_Pubmed_md/ner_assignment1/training/ner-transformer/model-best`. |
| Six sample papers | `/N/project/CoRSAL/L665_Assignment2_work/texts/` | The texts are the papers. Licenses are in `sources_sample.csv`. |
| Full 378-document corpus | `submission.zip` in `/N/project/CoRSAL/L665_Assignment1_submit/`, folder `cp_dysarthria_ner/texts/` | Same license limit. Google Drive folder shared by Shintaro: `https://drive.google.com/drive/folders/1veHeoPdCtVFdHXP54M6jjUaV6OKBb2_-`. |
| REALLMS key | environment variable `REALLMS_API_KEY` | Never commit it. |

`sources_sample.csv` is metadata only (ids, titles, URLs, licenses). The six documents are:

- `pubmed_32604092` Pausing and Sentence Stress in Children with Dysarthria due to Cerebral Palsy
- `pubmed_29184336` Speech Signal Analysis and Pattern Recognition in Diagnosis of Dysarthria
- `pubmed_33190131` Evaluation of an Automatic Speech Recognition Platform for Dysarthric Speech
- `arxiv_1506.02170` Hybridized Feature Extraction and Acoustic Modelling Approach for Dysarthric Speech Recognition
- `arxiv_1811.11101` Learning to detect dysarthria from raw speech
- `arxiv_1907.04743` Interpretable Deep Learning Model for the Detection and Reconstruction of Dysarthric Speech

## Schema

Entity types are the Assignment 1 labels: `DISORDER`, `SPEECH_FEATURE`, `ASSESSMENT`, `TREATMENT`, `SPEECH_TECH`, `DATASET`. Predicates are `has_feature`, `measures`, `treats`, `evaluated_on`, and `applied_to`. Negated or modal statements are qualified `rdf:Statement` nodes, not bare facts. Details and examples are in [schema.md](schema.md). The LLM prompt is in [prompts/extraction_prompt.md](prompts/extraction_prompt.md).

## How a teammate reruns it

1. Copy the six texts out of `submission.zip` into `/N/project/CoRSAL/L665_Assignment2_work/texts/{doc_id}.txt`.
2. Unzip `model-best.zip` so `config.cfg` is at `/N/project/CoRSAL/L665_Assignment2_work/model-best/config.cfg`.
3. The parser is `en_core_web_sm`. The course environment at `/N/project/ontology_learning/L665/envs/spacy-ner` has that model, but it does not have `en_core_web_trf`, and importing it from a login node stalled on the shared filesystem. The run that produced these graphs used a separate virtualenv with spaCy 3.8 and CPU PyTorch, which is what `requirements.txt` records. Domain labels come from Assignment 1's `model-best`. Dependency cues supply the predicate. The default spaCy labels are not forced into the six domain types.
4. The LLM call reuses the course client in `/N/project/ontology_learning/L665/L665/code/LLMs/REALLMS.ipynb` and the working copy in `/N/project/CoRSAL/L645/src/llm_tagger.py`: `OpenAI(base_url="https://reallms.rescloud.iu.edu/direct/v1")`, model `qwen3.8-27b`, temperature 0. Export `REALLMS_API_KEY` first. L645 already listed this model on 7 November 2026.
5. From `assignment2/`, build one virtualenv and run both extractors. Do not pip-install into the shared course environment.

```bash
PY=/N/soft/sles15sp6/python/gnu/3.12.11/bin/python3
VENV=/N/project/CoRSAL/L665_Assignment2_work/venv
$PY -m venv $VENV
$VENV/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
$VENV/bin/pip install -r requirements.txt
$VENV/bin/python -m spacy download en_core_web_sm
sbatch spacy_extract.slurm
set -a; source ~/.reallms_secrets; set +a
$VENV/bin/python scripts/llm_extract.py
$VENV/bin/python scripts/to_turtle.py
$VENV/bin/python scripts/graph_query.py
```

Open `graphs/spacy_output.ttl` and `graphs/llm_output.ttl` in Turtle Graph Studio (`code/graphs/turtle-visualizer` in the course repo) and in Protégé. `evaluation/inspection_notes.md` records the counts, the SPARQL query, and the label-search subgraphs.

## Assignment 1, for the same submission set

Canvas files for Assignment 1 are the three files in `/N/project/CoRSAL/L665_Assignment1_submit/`: `submission.zip`, `model-best.zip`, and `report.docx`. Upload those. Do not add the zip or the model to this repo. The report lists the same team.
