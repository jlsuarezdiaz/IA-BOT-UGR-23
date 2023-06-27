#!/bin/bash
#SBATCH -p muylarga
#SBATCH -c 2
#SBATCH --mem=10G
#SBATCH -o slurm_outputs/%A.out
#SBATCH -e slurm_outputs/%A.err

DB_FOLDER='evals'
ID=$SLURM_JOB_NAME
EVAL=$1

# cd the directory db/{job_name}, where job_name is the name of the slurm job.
cd $DB_FOLDER/$ID/$EVAL
# Copy the scripts to the working directory.
cp ../../../uncompress.py .
cp ../../../recopilate.py .

# Call the uncompress script.
python uncompress.py $ID

# If the uncompress script fails, exit.
if [ $? -ne 0 ]; then
    # Remove the eval folder.
    cd ..
    rm -rf $EVAL
    exit 1
fi

# Clone the repository
while ! git clone git@github.com:rbnuria/ParchisIA-23-solved.git
do
    sleep 1
done

# Create a softwares folder
mkdir softwares
mkdir results

# For each subfolder in the entregas folder, create a subfolder in the softwares folder.
for folder in entregas/*; do
    if [ -d "$folder" ]; then
        # Run the evaluation script.
        sbatch -J "$(basename "$folder")" ../../../run_evaluations.sh "$(basename "$folder")" $ID $EVAL
    fi
done

# Wait for the evaluations to finish.
python recopilate.py $ID $EVAL

cd ..
rm -rf $EVAL