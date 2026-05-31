"""Collect Slurm job information."""

from __future__ import annotations

import shutil
import subprocess

from realmon.models import SlurmJob


def is_slurm_available() -> bool:
    """Check if Slurm (squeue) is available on this system."""
    return shutil.which("squeue") is not None


def parse_squeue_output(output: str) -> list[SlurmJob]:
    """Parse squeue output in pipe-delimited format.

    Expected format from: squeue -h -o "%i|%u|%T|%M|%D|%C|%R|%j"
    Fields: JobID|User|State|Runtime|NumNodes|NumCPUs|Reason/NodeList|JobName
    """
    jobs: list[SlurmJob] = []

    for line in output.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split("|")
        if len(parts) < 8:
            continue

        jobs.append(
            SlurmJob(
                job_id=parts[0].strip(),
                user=parts[1].strip(),
                state=parts[2].strip(),
                runtime=parts[3].strip(),
                alloc_cpus=parts[5].strip(),
                nodelist_or_reason=parts[6].strip(),
                job_name=parts[7].strip(),
            )
        )

    return jobs


def collect_slurm_jobs() -> list[SlurmJob]:
    """Collect current Slurm jobs.

    Returns empty list if Slurm is not available or fails.
    """
    if not is_slurm_available():
        return []

    try:
        result = subprocess.run(
            ["squeue", "-h", "-o", "%i|%u|%T|%M|%D|%C|%R|%j"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []
        return parse_squeue_output(result.stdout)
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
        return []


def get_job_work_dir(job_id: str) -> str:
    """Try to get the working directory of a Slurm job via scontrol."""
    if not shutil.which("scontrol"):
        return ""

    try:
        result = subprocess.run(
            ["scontrol", "show", "job", job_id],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return ""

        for line in result.stdout.splitlines():
            for field in line.split():
                if field.startswith("WorkDir="):
                    return field[len("WorkDir="):]
        return ""
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError):
        return ""
