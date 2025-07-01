import os

def write_bash(job_name, command, logname=None, slurm=True, memory="4G", time="01:00:00"):
    """Writes a bash script for submitting a job to a cluster.

    Parameters:
    job_name : str
        The name of the job.
    command : str
        The command to run in the job.
    logname : str, optional
        The name of the log file. If not provided, defaults to job_name.log.
    slurm : bool, optional
        If True, writes a SLURM script instead of a SGE script. Defaults to True.
        if False, writes a QSUB script.
    """
    path = f"bSub_runMe/cuwalid_run_{job_name}.bash"
    log_file = logname or f"{job_name}.log"

    if slurm:
        lines = [
            "#!/bin/bash\n",
            f"#SBATCH --job-name=cuwalid_{job_name}\n",
            f"#SBATCH --time={time}\n",
            f"#SBATCH --mem={memory}\n",
            "#SBATCH --cpus-per-task=1\n",
            "#SBATCH --output=../bSub_logMe/%x.log\n",
            "#SBATCH --error=../bSub_logMe/%x.err\n",
            "\n",
            "module load miniconda3\n",
            "source activate test_cwld\n",
            f"{command} > ../bSub_logMe/{log_file} 2>&1\n"
        ]
    else:
        lines = [
            "#!/bin/bash\n",
            f"#$ -N cuwalid_{job_name}\n",
            f"#$ -l h_rt={time}\n",
            f"#$ -l h_vmem={memory}\n",
            "#$ -pe smp 1\n",
            "#$ -cwd\n",
            "#$ -j y\n",
            "#$ -V\n",
            "#$ -S /bin/bash\n",
            "\n",
            "source ~/miniconda3/bin/activate\n",
            "conda activate cwld\n",
            f"{command} > ../bSub_logMe/{log_file} 2>&1\n"
    ]
    with open(path, "w") as f:
        f.writelines(lines)

def main():
    os.makedirs("bSub_runMe", exist_ok=True)
    os.makedirs("bSub_logMe", exist_ok=True)

    # Only run STORM and StoPET jobs, since post-processing is now integrated
    write_bash("storm", "python -m cuwalid.storm.main_storm input_storm.json")
    write_bash("stopet", "python -m cuwalid.stopet.main_stopet_wrapper input_stopet.json")

    # Dryp jobs are generated separately later
    print("Run `submit_all.sh` after generating dryp_jsons.txt.")

if __name__ == "__main__":
    main()
