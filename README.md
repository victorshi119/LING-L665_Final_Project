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

## Licensing

`license` is the license each author chose. Most papers use
`arxiv.org/licenses/nonexclusive-distrib/1.0/`, which lets arXiv distribute the
paper but does not let us redistribute it. Keep those PDFs within the course
project folder. Papers under CC BY / CC BY-SA can be shared more freely.
