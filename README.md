# L665 – CP-associated spastic dysarthria corpus (Victor & Shintaro)

Staging area for the L665 corpus-construction phase. Code stays here; only the
cleaned data is copied to `/N/project/ontology_learning/L665/data/`.

## Layout

```
L665_Victor_Shintaro/
├── code/
│   ├── scrapers/     scrape_arxiv.py, arxiv_queries.json
│   ├── processing/   (todo) pdf → markdown, cleaning, dedupe, corpus.jsonl
│   └── slurm/        batch versions of the scrapers
├── data/
│   ├── raw/arxiv/    metadata.jsonl, pdfs/, manifest.json
│   └── processed/
└── logs/
```

## arXiv

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

## PDF → Markdown

`processing/pdf_folder_to_markdown.py` is copied unchanged from the course repo
(dcavar/L665 `code/Data/slurm_scripts/`, by Damir Cavar). It uses spaCy Layout/Docling
and writes `foo.md` beside each `foo.pdf`. `slurm/pdf_to_markdown.slurm` is a
BigRed200 version of the repo's Quartz script: `gpu` partition, one worker per
allocated GPU, and it refuses paths under the shared L665 folder.

One-time environment setup (already done in `envs/spacy-layout`):

```bash
module load python/3.12.11
python3 -m venv $B/envs/spacy-layout && source $B/envs/spacy-layout/bin/activate
pip install -r $B/code/processing/requirements.txt
```

```bash
# short test
sbatch -p gpu-debug -t 0:30:00 $B/code/slurm/pdf_to_markdown.slurm /N/scratch/$USER/l665_pdf2md_test
# full run (skips PDFs that already have a .md)
sbatch $B/code/slurm/pdf_to_markdown.slurm $B/data/raw/arxiv/pdfs
```

The Docling models are cached in `envs/hf_cache`. The first run downloads them.

## Cleaned corpus

`processing/build_arxiv_corpus.py` combines `metadata.jsonl` with the `.md` files. It removes
conversion artifacts and reference/acknowledgement sections, counts tokens, and writes
`data/processed/arxiv_corpus.jsonl` and `arxiv_corpus_stats.json`. `data/CORPUS.md`
documents the corpus (counts, sources, licensing, known issues).

```bash
source $B/envs/spacy-layout/bin/activate
python -I $B/code/processing/build_arxiv_corpus.py $B/data/raw/arxiv $B/data/processed
```

## Licensing

`license` is the license each author chose. Most papers use
`arxiv.org/licenses/nonexclusive-distrib/1.0/`, which lets arXiv distribute the
paper but does not let us redistribute it. Keep those PDFs within the course
project folder. Papers under CC BY / CC BY-SA can be shared more freely.
