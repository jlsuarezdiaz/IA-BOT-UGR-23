#!/bin/bash
#SBATCH -p muylarga
#SBATCH -c 2
#SBATCH --mem=1G
#SBATCH -o ../../../../../slurm_outputs/%A.out
#SBATCH -e ../../../../../slurm_outputs/%A.err

FOLDER=$1
ID=$2
EVAL=$3
PLAYER=$4
NINJA_ID=$5

# Run the tests.
export PATH="/home/profesia/anaconda/condabin:$PATH"
eval "$(conda shell.bash hook)"
conda activate IA

python run_tests_eval.py "$FOLDER" $ID $EVAL $PLAYER $NINJA_ID