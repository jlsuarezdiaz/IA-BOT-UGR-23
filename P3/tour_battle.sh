#!/bin/bash
#SBATCH -p muylarga
#SBATCH -c 6
#SBATCH --mem=1G
#SBATCH -o slurm_outputs/%A.out
#SBATCH -e slurm_outputs/%A.err
#SBATCH -x node19

P1_ID=$1
P2_ID=$2
DATE=$3

SOFTWARE_FOLDER='tour-executions'
RESULTS_FOLDER='tour-results'

# Check if the folder $SOFTWARE_FOLDER/$P1_ID doesn't contain the executable ParchisGame.
#if [ ! -f "$SOFTWARE_FOLDER/$P1_ID/ParchisGame" ]
#then
    # If it doesn't, do cmake and make.
#    cd $SOFTWARE_FOLDER/$P1_ID
#    cmake -DCMAKE_BUILD_TYPE=Release .
#    make -j4
#    cd ../..
#fi

# Check if the folder $SOFTWARE_FOLDER/$P2_ID doesn't contain the executable ParchisGame.
#if [ ! -f "$SOFTWARE_FOLDER/$P2_ID/ParchisGame" ]
#then
    # If it doesn't, do cmake and make.
#    cd $SOFTWARE_FOLDER/$P2_ID
#    cmake -DCMAKE_BUILD_TYPE=Release .
#    make -j4
#    cd ../..
#fi

# Run the python script.
export PATH="/home/profesia/anaconda/condabin:$PATH"
eval "$(conda shell.bash hook)"
conda activate IA

python3 tour_battle.py $P1_ID $P2_ID "$DATE"