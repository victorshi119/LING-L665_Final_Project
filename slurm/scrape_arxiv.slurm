#!/bin/bash
# Scrape arXiv metadata, licenses and PDFs for all queries in arxiv_queries.json.
# Network-bound (arXiv allows one request per 3 s), so one CPU is enough.
# Resumable: re-submitting skips papers, licenses and PDFs already on disk.
# Usage: ARXIV_CONTACT=you@iu.edu sbatch scrape_arxiv.slurm
#SBATCH --job-name=l665_arxiv
#SBATCH --output=/N/project/CoRSAL/L665_Victor_Shintaro/logs/arxiv.%j.out
#SBATCH --error=/N/project/CoRSAL/L665_Victor_Shintaro/logs/arxiv.%j.err
#SBATCH --time=4:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --ntasks=1
#SBATCH --partition=general
#SBATCH -A r01360
set -uo pipefail
set -x
export PYTHONUNBUFFERED=1

BASE="/N/project/CoRSAL/L665_Victor_Shintaro"

module load python/3.12.11
python3 -I "${BASE}/code/scrapers/scrape_arxiv.py" "${BASE}/data/raw/arxiv" --licenses --pdfs
