# LING-L665 Final Project – CP-associated spastic dysarthria

Victor & Shintaro, L665 (Fall 2026). Course goal: text → information extraction →
knowledge graph/ontology for cerebral palsy (CP)-associated spastic dysarthria and,
more broadly, CP-related dysarthria.

This repo holds code only. The data lives on BigRed200:

- working copy: `/N/project/CoRSAL/L665_Victor_Shintaro/` (this repo is checked out as `code/`)
- shared with the class: `/N/project/ontology_learning/L665/data/CP_Dysarthria/`

The corpus write-up (counts, sources, licensing, known issues) is `data/CORPUS.md` in
both places.

## Layout

```
L665_Victor_Shintaro/
├── code/                 ← this repo
│   ├── scrapers/         scrape_arxiv.py, arxiv_queries.json
│   ├── processing/       build_arxiv_corpus.py, requirements.txt
│   │                     (+ pdf_folder_to_markdown.py from the course repo, not committed)
│   └── slurm/            scrape_arxiv.slurm, pdf_to_markdown.slurm
├── data/
│   ├── CORPUS.md
│   ├── raw/arxiv/        metadata.jsonl, manifest.json, pdfs/ (*.pdf + *.md)
│   └── processed/        arxiv_corpus.jsonl, arxiv_corpus_stats.json
├── envs/                 spacy-layout venv, hf_cache
└── logs/
```

The Slurm scripts use absolute paths under `/N/project/CoRSAL/L665_Victor_Shintaro` and
the `r01360` allocation. Change `BASE` and `-A` if you run them from somewhere else.

## 1. Scrape arXiv

The search terms are named queries in `scrapers/arxiv_queries.json`. Each paper
is stored once in `metadata.jsonl`, and its `matched_queries` lists every query
that found it. Use that field to narrow the corpus, e.g. to papers that match
`cp_speech` or `cerebral_palsy`.

```bash
module load python/3.12.11
B=/N/project/CoRSAL/L665_Victor_Shintaro

# quick test
python3 -I $B/code/scrapers/scrape_arxiv.py /tmp/arxiv_test --only cp_speech --max-per-query 5

# full run: metadata + licenses (OAI-PMH) + PDFs; safe to re-run, skips existing work
python3 -I $B/code/scrapers/scrape_arxiv.py $B/data/raw/arxiv --licenses --pdfs --contact you@iu.edu

# or as a batch job
ARXIV_CONTACT=you@iu.edu sbatch $B/code/slurm/scrape_arxiv.slurm
```

The script uses only the standard library. arXiv allows one request every
3 seconds, and the script enforces that.

Record fields: `arxiv_id, version, title, abstract, authors, published, updated,
primary_category, categories, doi, journal_ref, comment, abs_url, pdf_url,
license, matched_queries`.

## 2. PDF → Markdown

The converter is the course's `pdf_folder_to_markdown.py` (spaCy Layout/Docling).
It writes `foo.md` beside each `foo.pdf`. The course materials are all rights
reserved, so the converter is **not in this repo**. Copy it in from the course repo
(dcavar/L665, `code/Data/slurm_scripts/`); `.gitignore` keeps it out of commits:

```bash
cp <your L665 clone>/code/Data/slurm_scripts/pdf_folder_to_markdown.py $B/code/processing/
```

`slurm/pdf_to_markdown.slurm` is our BigRed200 version of the course's Quartz
script. It uses the `gpu` partition, runs one worker per allocated GPU, makes the
output group-readable, and refuses any path under the shared L665 folder.

One-time environment setup (already done in `$B/envs/spacy-layout`):

```bash
module load python/3.12.11
python3 -m venv $B/envs/spacy-layout && source $B/envs/spacy-layout/bin/activate
pip install -r $B/code/processing/requirements.txt
```

```bash
# short test
sbatch -p gpu-debug -t 0:30:00 $B/code/slurm/pdf_to_markdown.slurm /N/scratch/$USER/l665_pdf2md_test
# full run (skips PDFs that already have a .md); 321 PDFs took 27 min on one A100
sbatch -p gpu-interactive -t 2:00:00 $B/code/slurm/pdf_to_markdown.slurm $B/data/raw/arxiv/pdfs
```

The Docling models are cached in `envs/hf_cache`. The first run downloads them.

## 3. Build the cleaned corpus

`processing/build_arxiv_corpus.py` combines `metadata.jsonl` with the `.md` files. It removes
conversion artifacts and reference/acknowledgement sections, counts tokens, and writes
`data/processed/arxiv_corpus.jsonl` and `arxiv_corpus_stats.json`.

```bash
source $B/envs/spacy-layout/bin/activate
python -I $B/code/processing/build_arxiv_corpus.py $B/data/raw/arxiv $B/data/processed
```

## Licensing

The code in this repo is MIT-licensed (see `LICENSE`). The corpus is not part of
the repo. Each paper keeps the license its authors chose (field `license`):
150 papers use arXiv's non-exclusive license, which does not let us redistribute
them, and 166 are under Creative Commons. Do not commit or publish corpus files.
