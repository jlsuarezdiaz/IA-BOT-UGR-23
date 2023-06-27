#!/bin/bash
#SBATCH -p muylarga
#SBATCH -c 4
#SBATCH --mem=1G
#SBATCH -o ../../../../../slurm_outputs/%A.out
#SBATCH -e ../../../../../slurm_outputs/%A.err

ID=$1
DATE=$2
PLAYER=$3
HEURISTIC=$4
NINJA_ID=$5

# Run the tests.
export PATH="/home/profesia/anaconda/condabin:$PATH"
eval "$(conda shell.bash hook)"
conda activate IA

python run_tests.py $ID "$DATE" $PLAYER $HEURISTIC $NINJA_ID