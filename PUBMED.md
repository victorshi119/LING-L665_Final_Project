# PubMed part of the CP-associated spastic dysarthria corpus

PubMed counterparts of the arXiv scripts: `scrapers/scrape_pubmed.py` and
`processing/build_pubmed_corpus.py`. `build_pubmed_corpus.py` imports the cleaning
code from `build_arxiv_corpus.py`, so the two have to stay in the same folder.

## 1. Scrape PubMed

The queries are the seven from `arxiv_queries.json`, rewritten in PubMed syntax
(`QUERIES` in the script). For each query the script takes the top N hits by PubMed
relevance (default 50) and fetches their metadata and abstracts through NCBI
E-utilities. It then tries to download an open-access PDF for each paper, first
from the PMC Open Access subset on AWS and then from OpenAlex's open-access
locations. It does not go behind paywalls.

```bash
pip install requests
PUBMED_CONTACT=you@iu.edu python3 scrape_pubmed.py 50 data/raw/pubmed
```

Output in the output folder:

- `results.csv`: one row per paper with `pmid, pmcid, doi, title, authors, year,
  journal, matched_queries, oa_status, pdf_status, pdf_source, abstract`
- `pdfs/PMID<pmid>.pdf`
- `no_pdf.ris`: the papers without a PDF, for a reference manager

Re-running skips PDFs that are already on disk. PubMed's relevance ranking changes
over time, so a re-run may pick a slightly different top 50.

The 2026-10-13 run (top 50 per query) found 300 papers. 60 had a PDF, 126 were
paywalled and 114 had no open-access PDF. Total PubMed hits at the time:

| query | hits |
|---|---|
| cerebral_palsy | 38,169 |
| dysarthria | 9,926 |
| cp_speech | 1,594 |
| spastic_speech | 1,349 |
| dysarthric | 706 |
| motor_speech_disorder | 393 |
| dysarthric_corpora | 20 |

## 2. PDF → Markdown

Use the repo's `slurm/pdf_to_markdown.slurm` unchanged:

```bash
sbatch -p gpu-debug -t 0:30:00 $B/code/slurm/pdf_to_markdown.slurm $B/data/raw/pubmed/pdfs
```

## 3. Build the cleaned corpus

`results.csv` and `pdfs/` (with the `.md` files) must be in the same folder.

```bash
source $B/envs/spacy-layout/bin/activate
python -I $B/code/processing/build_pubmed_corpus.py $B/data/raw/pubmed $B/data/processed
```

This writes `pubmed_corpus.jsonl` and `pubmed_corpus_stats.json`. Each record has
`"id": "pubmed:<pmid>"` and `"source": "pubmed"`, so it can be combined with
`arxiv_corpus.jsonl`.

## Licensing

The scraper records OpenAlex's open-access status (`oa_status`: gold, green, hybrid,
bronze), not each paper's license. Bronze papers are free to read but have no open
license. Do not commit or publish corpus files.
