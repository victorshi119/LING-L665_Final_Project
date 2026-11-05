#!/bin/bash
#SBATCH --job-name=cp-ner-docbin
#SBATCH --account=r00998
#SBATCH --partition=general
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=logs/build_corpus-%j.out
#SBATCH --error=logs/build_corpus-%j.err

# Rule-annotate the corpus and write the train/dev/test DocBins (CPU only).
# The login node can be too contended for this (on 2026-11-03 it got ~5% of a core).
#
# Submit from ner_assignment1/:  sbatch build_corpus.slurm

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")}"

module purge
source "${SPACY_NER_ENV:-/N/slate/$USER/envs/spacy-ner}/bin/activate"

python build_corpus.py
