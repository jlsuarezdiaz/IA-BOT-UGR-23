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
# Copy the practica2 folder here.
cp -r practica2/* softwares/"$folder"
# Copy the jugador.cpp and jugador.hpp files from the entregas folder to the softwares folder.
cp entregas/"$folder"/jugador.cpp softwares/"$folder"/Comportamientos_Jugador
cp entregas/"$folder"/jugador.hpp softwares/"$folder"/Comportamientos_Jugador

cd softwares/"$folder"
cp ../../../../../motorlib/* ./src/motorlib
cp ../../../../../patches/* ./Comportamientos_Jugador
# Update the motorlib/motor_juego.cpp to modify its output.
sed -i 's/if (monitor\.mostrarResultados() and monitor\.getLevel() < 2)/if(false)/g; s/else if (monitor\.mostrarResultados() and monitor\.getLevel() < 4)/else if(false)/g' ./src/motorlib/motor_juego.cpp 

# Cmake
cmake -DCMAKE_BUILD_TYPE=Release .
# Compile
make clean
make

# Run the tests.
export PATH="/home/profesia/anaconda/condabin:$PATH"
eval "$(conda shell.bash hook)"
conda activate IA
cp ../../../../../run_tests_eval.py .
cp ../../../../../mapas/* mapas/
cp ../../../../../tests.json .
python run_tests_eval.py "$folder" $ID $EVAL

# Wait for the tests to finish.

# Remove the software folder
#cd ..
#rm -rf software

