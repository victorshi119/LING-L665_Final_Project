#!/bin/bash
#SBATCH --job-name=cp-ner-predict
#SBATCH --account=r00998
#SBATCH --partition=h100-single
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=logs/predict-%j.out
#SBATCH --error=logs/predict-%j.err

# Apply the trained model to all corpus documents (separate prediction DocBin), then
# compare predictions with the rule labels on the test split.
#
# Submit from ner_assignment1/ after training:  sbatch predict.slurm
# or chained:  sbatch --dependency=afterok:<train job id> predict.slurm

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")}"

module purge
module load cudatoolkit/12.6 2>/dev/null || true
source "${SPACY_NER_ENV:-/N/slate/$USER/envs/spacy-ner}/bin/activate"
export TOKENIZERS_PARALLELISM=false

python predict.py --gpu-id 0
python evaluate.py
