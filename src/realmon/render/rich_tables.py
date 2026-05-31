"""Rich table rendering for realmon."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from realmon.models import ProcessInfo, GpuInfo, SlurmJob, SystemSnapshot


console = Console()


def render_top_table(processes: list[ProcessInfo], limit: int = 30) -> None:
    """Render the top processes table."""
    table = Table(title="realmon top - Process Monitor")
    table.add_column("PID", style="cyan", justify="right")
    table.add_column("USER", style="green")
    table.add_column("CPU%", justify="right")
    table.add_column("CORE_EQ", justify="right")
    table.add_column("MEM_GB", justify="right")
    table.add_column("GPU", justify="right")
    table.add_column("GPU_MEM_MB", justify="right")
    table.add_column("CWD", style="dim", max_width=30, overflow="ellipsis")
    table.add_column("CMD", max_width=50, overflow="ellipsis")

    for proc in processes[:limit]:
        gpu_str = str(proc.gpu_id) if proc.gpu_id is not None else ""
        gpu_mem_str = f"{proc.gpu_memory_mb:.0f}" if proc.gpu_memory_mb else ""

        table.add_row(
            str(proc.pid),
            proc.user,
            f"{proc.cpu_percent:.1f}",
            f"{proc.core_equivalent:.2f}",
            f"{proc.memory_gib:.2f}",
            gpu_str,
            gpu_mem_str,
            proc.cwd,
            proc.command,
        )

    console.print(table)


def render_gpu_table(gpus: list[GpuInfo], processes: list[ProcessInfo]) -> None:
    """Render the GPU information table."""
    if not gpus:
        console.print("[yellow]No GPU information available (NVML not accessible)[/yellow]")
        return

    # GPU summary table
    table = Table(title="GPU Status")
    table.add_column("GPU", style="cyan", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Util%", justify="right")
    table.add_column("Mem Used (MiB)", justify="right")
    table.add_column("Mem Total (MiB)", justify="right")
    table.add_column("Temp °C", justify="right")

    for gpu in gpus:
        temp_str = f"{gpu.temperature_c:.0f}" if gpu.temperature_c is not None else "N/A"
        table.add_row(
            str(gpu.id),
            gpu.name,
            f"{gpu.utilization_percent:.0f}",
            f"{gpu.memory_used_mib:.0f}",
            f"{gpu.memory_total_mib:.0f}",
            temp_str,
        )

    console.print(table)

    # GPU processes table
    gpu_procs = [p for p in processes if p.gpu_id is not None]
    if gpu_procs:
        proc_table = Table(title="GPU Processes")
        proc_table.add_column("PID", style="cyan", justify="right")
        proc_table.add_column("USER", style="green")
        proc_table.add_column("GPU", justify="right")
        proc_table.add_column("GPU_MEM_MB", justify="right")
        proc_table.add_column("CWD", style="dim", max_width=30, overflow="ellipsis")
        proc_table.add_column("CMD", max_width=50, overflow="ellipsis")

        for proc in gpu_procs:
            proc_table.add_row(
                str(proc.pid),
                proc.user,
                str(proc.gpu_id) if proc.gpu_id is not None else "",
                f"{proc.gpu_memory_mb:.0f}" if proc.gpu_memory_mb else "",
                proc.cwd,
                proc.command,
            )

        console.print(proc_table)


def render_slurm_table(jobs: list[SlurmJob]) -> None:
    """Render the Slurm jobs table."""
    if not jobs:
        console.print("[yellow]No Slurm jobs found or Slurm is not available[/yellow]")
        return

    table = Table(title="Slurm Jobs")
    table.add_column("JobID", style="cyan")
    table.add_column("User", style="green")
    table.add_column("State")
    table.add_column("JobName")
    table.add_column("CPUs", justify="right")
    table.add_column("Runtime")
    table.add_column("NodeList/Reason")
    table.add_column("WorkDir", style="dim", max_width=30, overflow="ellipsis")

    for job in jobs:
        table.add_row(
            job.job_id,
            job.user,
            job.state,
            job.job_name,
            job.alloc_cpus,
            job.runtime,
            job.nodelist_or_reason,
            job.work_dir,
        )

    console.print(table)


def render_user_table(processes: list[ProcessInfo], username: str) -> None:
    """Render processes for a specific user."""
    user_procs = [p for p in processes if p.user == username]

    if not user_procs:
        console.print(f"[yellow]No processes found for user '{username}'[/yellow]")
        return

    table = Table(title=f"Processes for user: {username}")
    table.add_column("PID", style="cyan", justify="right")
    table.add_column("CPU%", justify="right")
    table.add_column("CORE_EQ", justify="right")
    table.add_column("MEM_GB", justify="right")
    table.add_column("GPU", justify="right")
    table.add_column("GPU_MEM_MB", justify="right")
    table.add_column("CWD", style="dim", max_width=30, overflow="ellipsis")
    table.add_column("CMD", max_width=50, overflow="ellipsis")

    for proc in user_procs:
        gpu_str = str(proc.gpu_id) if proc.gpu_id is not None else ""
        gpu_mem_str = f"{proc.gpu_memory_mb:.0f}" if proc.gpu_memory_mb else ""

        table.add_row(
            str(proc.pid),
            f"{proc.cpu_percent:.1f}",
            f"{proc.core_equivalent:.2f}",
            f"{proc.memory_gib:.2f}",
            gpu_str,
            gpu_mem_str,
            proc.cwd,
            proc.command,
        )

    console.print(table)


def render_snapshot(snapshot: SystemSnapshot, limit: int = 30) -> None:
    """Render a full system snapshot."""
    render_top_table(snapshot.processes, limit=limit)
