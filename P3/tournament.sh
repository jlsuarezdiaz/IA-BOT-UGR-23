#!/bin/bash
#SBATCH -J TOURNAMENT
#SBATCH -p muylarga
#SBATCH -c 16
#SBATCH --mem=1G
#SBATCH -o slurm_outputs/%A.out
#SBATCH -e slurm_outputs/%A.err
#SBATCH -b 00:00

# Create the folder tour-executions if it does not exist.
mkdir -p tour-executions
cd tour-executions || exit

# Clone the repository. If it fails, retry until it succeeds.
while ! git clone git@github.com:rbnuria/ParchisIA-23-solved.git
do
    sleep 1
done

# Rename the repository to software.
mv ParchisIA-23-solved software

# For every folder inside ../tour-submissions, do the following:
for FOLDER in ../tour-submissions/*
do
    # Check if it contains the files AIPlayer.cpp and AIPlayer.h and metadata.json.
    if [ -f "$FOLDER/AIPlayer.cpp" ] && [ -f "$FOLDER/AIPlayer.h" ] && [ -f "$FOLDER/metadata.json" ]
    then
        # Create a folder with the name of the folder inside ../tour-executions.
        FOLDER_NAME=$(basename "$FOLDER")
        mkdir -p "$FOLDER_NAME"
        cd "$FOLDER_NAME"
        # Copy the software folder contents here.
        cp -r ../software/* .
        # Copy the files AIPlayer.cpp and AIPlayer.h from the parent folder to ./src and ./include, respectively.
        cp ../"$FOLDER"/AIPlayer.cpp ./src
        cp ../"$FOLDER"/AIPlayer.h ./include
        # Copy the metadata.json file to the current folder.
        cp ../"$FOLDER"/metadata.json .
        # Try to cmake and make. If it fails, remove the folder.
        cmake -DCMAKE_BUILD_TYPE=Release .
        make -j16
        if [ $? -ne 0 ]
        then
            cd ..
            rm -rf "$FOLDER_NAME"
        else
            cd ..
        fi

        #if ! cmake -DCMAKE_BUILD_TYPE=Release . && make -j16
        #then
        #    cd ..
        #    rm -rf "$FOLDER_NAME"
        #else
        #    cd ..
        #fi
    fi
done

export PATH="/home/profesia/anaconda/condabin:$PATH"
eval "$(conda shell.bash hook)"
conda activate IA

# Run the tournament.
cd ..
python tournament.py

# Move the folder tour-executions to the folder tour-executions-old/$(date +%Y-%m-%d_%H-%M-%S).
mv tour-executions tour-executions-old/"$(date +%Y-%m-%d_%H-%M-%S)"

# SCP the files tournament-results/battle_results.json and tournament-results/classification_table.json to the web server.
scp tournament-results/battle_results.json <WEB_SERVER>:<WEB_SERVER_PATH>/data/battle_results.json
scp tournament-results/classification_table.json <WEB_SERVER>:<WEB_SERVER_PATH>/data/classification_table.json

# Submit this script again to the queue.
sbatch tournament.sh

