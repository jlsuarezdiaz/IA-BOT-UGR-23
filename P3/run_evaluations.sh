#!/bin/bash
#SBATCH -p muylarga
#SBATCH -c 2
#SBATCH --mem=10G
#SBATCH -o ../../../slurm_outputs/%A.out
#SBATCH -e ../../../slurm_outputs/%A.err

folder=$1
ID=$2
EVAL=$3

mkdir softwares/"$folder"
# Copy the ParchisIA-23-solved folder here.
cp -r ParchisIA-23-solved/* softwares/"$folder"
# Copy the AIPlayer.cpp and AIPlayer.h files from the entregas folder to the softwares folder.
cp entregas/"$folder"/AIPlayer.cpp softwares/"$folder"/src
cp entregas/"$folder"/AIPlayer.h softwares/"$folder"/include

cd softwares/"$folder"

# Cmake
cmake -DCMAKE_BUILD_TYPE=Release .
# Compile
make clean
make

# Run the tests.
export PATH="/home/profesia/anaconda/condabin:$PATH"
eval "$(conda shell.bash hook)"
conda activate IA
cp ../../../../../run_ninja_eval.sh .
cp ../../../../../run_tests_eval.py .

# python run_ninjas_eval.py "$folder" $ID $EVAL
sbatch -J "1-1-$folder" run_ninja_eval.sh "$folder" $ID $EVAL 1 1
sbatch -J "2-1-$folder" run_ninja_eval.sh "$folder" $ID $EVAL 2 1
sbatch -J "1-2-$folder" run_ninja_eval.sh "$folder" $ID $EVAL 1 2
sbatch -J "2-2-$folder" run_ninja_eval.sh "$folder" $ID $EVAL 2 2
sbatch -J "1-3-$folder" run_ninja_eval.sh "$folder" $ID $EVAL 1 3
sbatch -J "2-3-$folder" run_ninja_eval.sh "$folder" $ID $EVAL 2 3
sbatch -J "1-4-$folder" run_ninja_eval.sh "$folder" $ID $EVAL 1 4
sbatch -J "2-4-$folder" run_ninja_eval.sh "$folder" $ID $EVAL 2 4

# Wait for the tests to finish.

# Remove the software folder
#cd ..
#rm -rf software