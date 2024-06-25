#!/bin/bash
#SBATCH --job-name=orpo
#SBATCH --partition=partition
#SBATCH --no-requeue
#SBATCH --gres=gpu:4
#SBATCH --nodes=1
#SBATCH --constraint=a100-80g
#SBATCH --mem=80GB
#SBATCH --time=6:00:00
#SBATCH -d singleton
#SBATCH --open-mode truncate
#SBATCH -o orpo.out
#SBATCH --mail-type=end 
#SBATCH --mail-user=<mail>

# Loading modules
module load cuda/11.8.0 python/3.11.0

# Running ORPO
ACCELERATE_LOG_LEVEL=info accelerate launch --config_file ../deepspeed_zero3.yaml run_orpo.py orpo.yaml