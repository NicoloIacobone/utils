#!/bin/bash
#
# Specify job name.
#SBATCH --job-name=anycam
#
# Specify output file.
#SBATCH --output=anycam_%j.log
#
# Specify error file.
#SBATCH --error=anycam_%j.err
#
# Specify open mode for log files.
#SBATCH --open-mode=append
#
# Specify time limit.
#SBATCH --time=01:00:00
#
# Specify number of tasks.
#SBATCH --ntasks=1
#
# Specify number of CPU cores per task.
#SBATCH --cpus-per-task=8
#
# Specify number of required GPUs.
#SBATCH --gpus=rtx_4090:2

echo "=== Job starting on $(hostname) at $(date) ==="
# DATE_VAR=$(date +%Y%m%d%H%M%S)

# Specify directories.
# export REPO="/cluster/work/igp_psr/niacobone/anycam"

# Load modules.
module load stack/2024-06 python/3.11 cuda/12.4 eth_proxy
echo "Loaded modules: $(module list 2>&1)"

# Activate virtual environment for SpatialTrackerV2.
source /cluster/work/igp_psr/niacobone/anycam/myenv/bin/activate
echo "Activated Python venv: $(which python)"

# Execute
cd /cluster/work/igp_psr/niacobone/anycam
echo "Starting AnyCam inference..."
python anycam/scripts/anycam_demo.py ++input_path=/cluster/work/igp_psr/niacobone/anycam/examples/nicola.mp4 ++model_path=pretrained_models/anycam_seq8 ++output_path=/cluster/work/igp_psr/niacobone/anycam/examples/results ++visualize=true ++rerun_mode=connect ++rerun_address=localhost:9876

echo "=== Job finished at $(date) ==="