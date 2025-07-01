#!/bin/bash
set -e

# Run this script to submit DRYP jobs on a Slurm HPC cluster.
# Ensure you have the necessary permissions and the conda environment is set up correctly.
# Ensure that STORM and StoPET jobs are submitted before running this script.

# Navigate to the directory with .bash files
pushd bSub_runMe

# Read Storm JSON files and submit jobs for each
while IFS= read -r dryp_json; do
    # Create a DRYP job script for each DRYP JSON
    job_name=$(basename "$dryp_json" .json)
    bash_script="dryp_${job_name}.bash"

    # Create the bash script for DRYP
    cat > "$bash_script" <<EOF
#!/bin/bash
#SBATCH --job-name=dryp_${job_name}
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=10:00:00
#SBATCH --mem=40G
#SBATCH --partition=cuwalid
#SBATCH --output=bSub_logMe/dryp_${job_name}.out
#SBATCH --error=bSub_logMe/dryp_${job_name}.error

source ~/miniconda3/bin/activate # Activate the conda environment
conda activate test_cwld # check if this is the correct environment

# Run DRYP model with the provided JSON path
python -m cuwalid.dryp.main_DRYP "$dryp_json" > bSub_logMe/dryp_${job_name}.log 2>&1
EOF
    # Make the script executable
    chmod +x "$bash_script"

    # Submit the DRYP job with dependency on both Storm and StoPET
    sbatch "$bash_script"

done < /home/cuwalid/training/forecast/regional/dryp_jsons.txt  # Path to your dryp_jsons.txt

popd