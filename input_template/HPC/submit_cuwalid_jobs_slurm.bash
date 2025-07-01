#!/bin/bash
set -e

# Navigate to the directory with .bash files
pushd bSub_runMe

# Read Storm JSON files and submit jobs for each
while IFS= read -r storm_json; do
    # Submit Storm job and get job ID
    storm_jobid=$(sbatch --export=STORM_JSON="$storm_json" --parsable cuwalid_run_storm.bash)

    # Submit StoPET job for the same JSON
    stopet_json=$(echo "$storm_json" | sed 's/storm/stopet/')
    stopet_jobid=$(sbatch --export=STOPET_JSON="$stopet_json" --parsable cuwalid_run_stopet.bash)

    # Now submit DRYP jobs after Storm and StoPET (they should wait until both are done)
    while IFS= read -r dryp_json; do
        job_name=$(basename "$dryp_json" .json)
        bash_script="bSub_runMe/dryp_${job_name}.bash"

        # Create the bash script for DRYP
        cat > "$bash_script" <<EOF
#!/bin/bash
#SBATCH --job-name=dryp_${job_name}
#SBATCH --time=6:00:00
#SBATCH --mem=40G
#SBATCH --ntasks-per-node=1
#SBATCH --partition=cuwalid
#SBATCH --output=bSub_logMe/dryp_${job_name}.out
#SBATCH --error=bSub_logMe/dryp_${job_name}.error
#SBATCH --export=ALL

source ~/miniconda3/bin/activate
conda activate cwld

# Run the DRYP command with the provided JSON
python -m cuwalid.dryp "$dryp_json"
EOF

        chmod +x "$bash_script"

        # Submit the DRYP job with dependency on both Storm and StoPET
        sbatch --dependency=afterok:$storm_jobid:$stopet_jobid "$bash_script"
    done < path/to/dryp_jsons.txt

done < path/to/storm_jsons.txt

popd
