#!/bin/bash
# BigRed200 port of dcavar/L665 code/Data/slurm_scripts/convert_pdfs_quartz.slurm.
# Converts every PDF in PDF_FOLDER to a .md beside it with spaCy Layout/Docling,
# one worker per allocated GPU (1 by default; ask for more with --gres=gpu:N).
# Resumable: PDFs that already have a .md are skipped (pass --overwrite to redo).
# Usage: sbatch pdf_to_markdown.slurm PDF_FOLDER [converter options]
#   e.g. sbatch pdf_to_markdown.slurm /N/project/CoRSAL/L665_Victor_Shintaro/data/raw/arxiv/pdfs
#        sbatch -p gpu-debug -t 0:30:00 pdf_to_markdown.slurm SOME_TEST_FOLDER
#SBATCH --job-name=l665_pdf2md
#SBATCH --output=/N/project/CoRSAL/L665_Victor_Shintaro/logs/pdf2md.%j.out
#SBATCH --error=/N/project/CoRSAL/L665_Victor_Shintaro/logs/pdf2md.%j.err
#SBATCH --time=8:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH -A r01360
set -uo pipefail
set -x
export PYTHONUNBUFFERED=1

BASE="/N/project/CoRSAL/L665_Victor_Shintaro"
LOGS="${BASE}/logs"
PYTHON_SCRIPT="${BASE}/code/processing/pdf_folder_to_markdown.py"
ENV="${SPACY_LAYOUT_ENV:-${BASE}/envs/spacy-layout}"

if (( $# < 1 )); then
    echo "Usage: sbatch $0 PDF_FOLDER [converter options]" >&2
    exit 2
fi
PDF_FOLDER="$(realpath "$1")"
shift

# The converter writes .md files next to the PDFs; never let it touch the shared class folder.
if [[ "${PDF_FOLDER}" == /N/project/ontology_learning/* ]]; then
    echo "Refusing to write into the shared L665 folder: ${PDF_FOLDER}" >&2
    exit 2
fi

# Docling downloads its layout/table/OCR models from Hugging Face on first use.
export HF_HOME="${BASE}/envs/hf_cache"
export TMPDIR="/N/scratch/${USER}/tmp"
mkdir -p "${HF_HOME}" "${TMPDIR}"

module load python/3.12.11
module load cudatoolkit/12.2 2>/dev/null || true
source "${ENV}/bin/activate"

python -c 'import torch; assert torch.cuda.is_available(), "no CUDA device visible"; print(torch.cuda.device_count(), "GPU(s):", torch.cuda.get_device_name(0))' || exit 2

IFS=',' read -r -a GPU_IDS <<< "${CUDA_VISIBLE_DEVICES:-0}"
NUM=${#GPU_IDS[@]}
THREADS=$(( ${SLURM_CPUS_PER_TASK:-16} / NUM ))
export OMP_NUM_THREADS=${THREADS} OPENBLAS_NUM_THREADS=${THREADS} MKL_NUM_THREADS=${THREADS}
export TOKENIZERS_PARALLELISM=false

declare -a PIDS=()
for (( worker=0; worker<NUM; worker++ )); do
    worker_log="${LOGS}/pdf2md.${SLURM_JOB_ID}.gpu${worker}.log"
    CUDA_VISIBLE_DEVICES="${GPU_IDS[$worker]}" \
        python "${PYTHON_SCRIPT}" "${PDF_FOLDER}" \
            --device cuda \
            --num-threads "${THREADS}" \
            --num-shards "${NUM}" \
            --shard-index "${worker}" \
            "$@" >"${worker_log}" 2>&1 &
    PIDS+=("$!")
done

status=0
for (( worker=0; worker<NUM; worker++ )); do
    if ! wait "${PIDS[$worker]}"; then
        echo "Shard ${worker}/${NUM} had failures; see ${LOGS}/pdf2md.${SLURM_JOB_ID}.gpu${worker}.log" >&2
        status=1
    fi
done

# The converter writes through mkstemp, which leaves .md files owner-only (600);
# open them up to the group so teammates and the class can read them.
find "${PDF_FOLDER}" -name '*.md' ! -perm -g=r -exec chmod g+rw {} +
exit "${status}"
