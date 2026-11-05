#!/bin/bash
#SBATCH --job-name=cp-ner-gpucheck
#SBATCH --account=r00998
#SBATCH --partition=h100-debug
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:10:00
#SBATCH --output=logs/gpu_check-%j.out
# Quick check that the env's CuPy (CUDA 12) and PyTorch builds both work on an H100 node.
set -euo pipefail
module purge
module load cudatoolkit/12.6 2>/dev/null || true
source "${SPACY_NER_ENV:-/N/slate/$USER/envs/spacy-ner}/bin/activate"
nvidia-smi
python - <<'PY'
import torch, cupy, spacy, thinc
print("torch", torch.__version__, "cuda", torch.version.cuda, "available", torch.cuda.is_available())
print("cupy", cupy.__version__, "devices", cupy.cuda.runtime.getDeviceCount())
print("spacy gpu", spacy.require_gpu(0))
x = torch.randn(1000, 1000, device="cuda"); print("torch matmul ok", float((x @ x).sum()) != 0)
y = cupy.random.randn(1000, 1000); print("cupy matmul ok", float((y @ y).sum()) != 0)
PY
