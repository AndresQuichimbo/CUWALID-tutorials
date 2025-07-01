#!/bin/bash
set -e

# Navigate to the directory with .bash files
pushd bSub_runMe

# Read Storm JSON files and submit jobs for each
while IFS= read -r storm_json; do
    # Create a DRYP job script for each DRYP JSON
    job_name=$(basename "$storm_json" .json)
    bash_script="storm_${job_name}.bash"

    # Create the bash script for DRYP
    cat > "$bash_script" <<EOF
#!/bin/bash
#SBATCH --job-name=storm_${job_name}
#SBATCH --time=6:00:00
#SBATCH --mem=40G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=cuwalid
#SBATCH --output=bSub_logMe/storm_${job_name}.out
#SBATCH --error=bSub_logMe/storm_${job_name}.error
#SBATCH --export=ALL

source ~/miniconda3/bin/activate # Activate the conda environment
conda activate test_cwld # check if this is the correct environment

# Run DRYP model with the provided JSON path
python -m cuwalid.storm.main_storm "$storm_json" > bSub_logMe/storm_${job_name}.log 2>&1
EOF
    # Make the script executable
    chmod +x "$bash_script"

    # Submit the CUWALID Storm
    sbatch "$bash_script"

done < /home/cuwalid/training/forecast/regional/storm_jsons.txt

# Read stoPET JSON files and submit jobs for each
while IFS= read -r stopet_json; do
    # Create a DRYP job script for each DRYP JSON
    job_name=$(basename "$stopet_json" .json)
    bash_script="stopet_${job_name}.bash"

    # Create the bash script for DRYP
    cat > "$bash_script" <<EOF
#!/bin/bash
#SBATCH --job-name=stopet_${job_name}
#SBATCH --time=6:00:00
#SBATCH --mem=40G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=cuwalid
#SBATCH --output=bSub_logMe/stopet_${job_name}.out
#SBATCH --error=bSub_logMe/stopet_${job_name}.error
#SBATCH --export=ALL

source ~/miniconda3/bin/activate # Activate the conda environment
conda activate test_cwld # check if this is the correct environment

# Run DRYP model with the provided JSON path
python -m cuwalid.stopet.main_stopet_wrapper "$stopet_json" > bSub_logMe/stopet_${job_name}.log 2>&1
EOF
    # Make the script executable
    chmod +x "$bash_script"

    # Submit the CUWALID StoPET
    sbatch "$bash_script"

done < /home/cuwalid/training/forecast/regional/stopet_jsons.txt

popd