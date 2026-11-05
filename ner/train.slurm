#!/bin/bash
#SBATCH --job-name=cp-ner-train
#SBATCH --account=r00998
#SBATCH --partition=h100-single
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=logs/train-%j.out
#SBATCH --error=logs/train-%j.err

# Train the transformer NER model on the rule-annotated DocBins from build_corpus.py.
# Same recipe as the course script (L665 code/NER/slurm_scripts/train_transformer_quartz.py):
# `spacy init config --pipeline transformer,ner --optimize accuracy --gpu`, then `spacy train`
# and `spacy evaluate`; but on one GPU, with our fixed document-level train/dev/test split.
#
# Submit from ner_assignment1/:  sbatch train.slurm
# Short test run (extra arguments go to `spacy train`):
#   OUT=training/ner-smoke SKIP_DEBUG_DATA=1 sbatch --partition=h100-debug --time=00:55:00 \
#       --job-name=cp-ner-smoke train.slurm --training.max_steps 300 --training.eval_frequency 100

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")}"

module purge
module load cudatoolkit/12.6 2>/dev/null || true
source "${SPACY_NER_ENV:-/N/slate/$USER/envs/spacy-ner}/bin/activate"
export TOKENIZERS_PARALLELISM=false

OUT="${OUT:-training/ner-transformer}"
mkdir -p "$OUT"
nvidia-smi
python -m spacy info

if [[ ! -f training/config.cfg ]]; then
    python -m spacy init config training/config.cfg --lang en \
        --pipeline transformer,ner --optimize accuracy --gpu --force
fi

# Papers are thousands of tokens long; max_length=500 makes the corpus reader train on
# sentences (boundaries are stored in the DocBins) instead of whole documents.
# (debug data can't run on the login node: the tokenizer's thread pool hits the per-user limit there.)
if [[ "${SKIP_DEBUG_DATA:-0}" != 1 ]]; then
    python -m spacy debug data training/config.cfg \
        --paths.train corpus/train.spacy --paths.dev corpus/dev.spacy \
        --corpora.train.max_length 500 --corpora.dev.max_length 500 \
        2>&1 | tee "$OUT/debug_data.log" || true
fi

python -m spacy train training/config.cfg --output "$OUT" --gpu-id 0 \
    --paths.train corpus/train.spacy --paths.dev corpus/dev.spacy \
    --corpora.train.max_length 500 --corpora.dev.max_length 500 \
    "$@" 2>&1 | tee "$OUT/train.log"

python -m spacy evaluate "$OUT/model-best" corpus/test.spacy \
    --output "$OUT/test_metrics.json" --gpu-id 0
