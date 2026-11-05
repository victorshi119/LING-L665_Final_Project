#!/bin/bash
# Create the Python 3.12 environment used for every step of this project (Quartz).
# Mirrors L665 code/NER/slurm_scripts/requirements.txt, but in the user's own space.
set -euo pipefail

ENV_DIR="${SPACY_NER_ENV:-/N/slate/$USER/envs/spacy-ner}"

module purge
module load gnu/12.2.0 python/3.12.4   # python/3.12.4 needs a gnu module on Quartz

python3.12 -m venv "$ENV_DIR"
source "$ENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install "spacy[transformers,cuda12x]==3.8.16" pytextrank pandas
python -m spacy download en_core_web_sm

python -c 'from importlib.metadata import version as v; print("spaCy", v("spacy"), "| spacy-transformers", v("spacy-transformers"), "| torch", v("torch"))'
