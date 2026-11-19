#!/bin/bash
# Domain NER plus dependency rules for the six-document sample.
# The course env is large, so this runs on a compute node rather than the login node.
#SBATCH --job-name=l665_a2_spacy
#SBATCH --output=/N/project/CoRSAL/L665_Victor_Shintaro/logs/a2_spacy.%j.out
#SBATCH --error=/N/project/CoRSAL/L665_Victor_Shintaro/logs/a2_spacy.%j.err
#SBATCH --time=01:30:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --ntasks=1
#SBATCH --partition=general
#SBATCH -A r01360
set -euo pipefail
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=""
cd /N/project/CoRSAL/L665_Victor_Shintaro/code/assignment2
/N/project/CoRSAL/L665_Assignment2_work/venv/bin/python scripts/spacy_extract.py
