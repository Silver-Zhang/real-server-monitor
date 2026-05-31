"""CLI entry point for realmon."""

from __future__ import annotations

import datetime
import platform
import time
from typing import Optional

import typer
from rich.console import Console

from realmon.collectors.gpu_nvml import collect_gpu_info, get_all_gpu_processes
from realmon.collectors.psutil_collector import (
    collect_cpu_info,
    collect_memory_info,
    collect_processes,
)
from realmon.collectors.slurm import collect_slurm_jobs
from realmon.models import SystemSnapshot
from realmon.render.json_output import render_json
from realmon.render.rich_tables import (
    render_gpu_table,
    render_slurm_table,
    render_top_table,
    render_user_table,
)

app = typer.Typer(help="realmon - Server resource monitor CLI tool")
console = Console()


def _collect_snapshot() -> SystemSnapshot:
    """Collect a full system snapshot."""
    cpu = collect_cpu_info()
    memory = collect_memory_info()
    gpus = collect_gpu_info()
    processes = collect_processes()
    slurm_jobs = collect_slurm_jobs()

    # Associate GPU processes with CPU processes
    gpu_procs = get_all_gpu_processes(gpus)
    gpu_proc_map: dict[int, tuple[int, float]] = {}
    for gp in gpu_procs:
        gpu_proc_map[gp.pid] = (gp.gpu_id, gp.gpu_memory_mb)

    for proc in processes:
        if proc.pid in gpu_proc_map:
            proc.gpu_id, proc.gpu_memory_mb = gpu_proc_map[proc.pid]

    return SystemSnapshot(
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        host=platform.node(),
        cpu=cpu,
        memory=memory,
        gpus=gpus,
        processes=processes,
        slurm_jobs=slurm_jobs,
    )


def _sort_processes(snapshot: SystemSnapshot, sort_key: str) -> None:
    """Sort processes in a snapshot based on the given key."""
    if sort_key == "gpu":
        snapshot.processes.sort(
            key=lambda p: (p.gpu_memory_mb or 0), reverse=True
        )
    elif sort_key == "mem":
        snapshot.processes.sort(key=lambda p: p.memory_gib, reverse=True)
    elif sort_key == "cpu":
        snapshot.processes.sort(key=lambda p: p.cpu_percent, reverse=True)
    else:
        # Default: GPU first, then CPU, then memory
        snapshot.processes.sort(
            key=lambda p: (
                -(p.gpu_memory_mb or 0),
                -p.cpu_percent,
                -p.memory_gib,
            )
        )


@app.command()
def top(
    sort: str = typer.Option("default", help="Sort by: cpu, mem, gpu, default"),
    limit: int = typer.Option(30, help="Number of processes to display"),
) -> None:
    """Show top processes by resource usage."""
    snapshot = _collect_snapshot()
    _sort_processes(snapshot, sort)
    render_top_table(snapshot.processes, limit=limit)


@app.command()
def gpu() -> None:
    """Show GPU usage and GPU processes."""
    snapshot = _collect_snapshot()
    render_gpu_table(snapshot.gpus, snapshot.processes)


@app.command()
def slurm() -> None:
    """Show current Slurm jobs."""
    jobs = collect_slurm_jobs()
    render_slurm_table(jobs)


@app.command()
def user(username: str = typer.Argument(..., help="Username to filter")) -> None:
    """Show processes for a specific user."""
    snapshot = _collect_snapshot()
    _sort_processes(snapshot, "default")
    render_user_table(snapshot.processes, username)


@app.command(name="json")
def json_output() -> None:
    """Output full system snapshot as JSON."""
    snapshot = _collect_snapshot()
    _sort_processes(snapshot, "default")
    console.print(render_json(snapshot), highlight=False)


@app.command()
def watch(
    interval: float = typer.Option(2.0, help="Refresh interval in seconds"),
    sort: str = typer.Option("default", help="Sort by: cpu, mem, gpu, default"),
    limit: int = typer.Option(30, help="Number of processes to display"),
) -> None:
    """Watch mode - refresh monitoring at regular intervals."""
    try:
        while True:
            console.clear()
            snapshot = _collect_snapshot()
            _sort_processes(snapshot, sort)
            render_top_table(snapshot.processes, limit=limit)
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped.[/dim]")


if __name__ == "__main__":
    app()
