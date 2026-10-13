#!/bin/bash
#SBATCH -J l665_arxiv
#SBATCH -A r01024
#SBATCH -p general
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=04:00:00
#SBATCH -o /N/project/CoRSAL/L665_Victor_Shintaro/logs/%x_%j.out

# Scrape arXiv metadata, licenses and PDFs for all queries in arxiv_queries.json.
# Network-bound (arXiv allows one request per 3 s), so one CPU is enough.
# Usage: ARXIV_CONTACT=you@iu.edu sbatch code/slurm/scrape_arxiv.slurm

BASE=/N/project/CoRSAL/L665_Victor_Shintaro
module load python/3.12.11
python3 -I "$BASE/code/scrapers/scrape_arxiv.py" "$BASE/data/raw/arxiv" --licenses --pdfs
