"""Data models for realmon."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProcessInfo(BaseModel):
    """Information about a single process."""

    pid: int
    user: str = ""
    cpu_percent: float = 0.0
    core_equivalent: float = 0.0
    memory_gib: float = 0.0
    command: str = ""
    name: str = ""
    cwd: str = ""
    start_time: str | None = None
    gpu_id: int | None = None
    gpu_memory_mb: float | None = None
    slurm_job_id: str | None = None


class GpuProcessInfo(BaseModel):
    """GPU process information."""

    pid: int
    gpu_id: int
    gpu_memory_mb: float


class GpuInfo(BaseModel):
    """Information about a single GPU."""

    id: int
    name: str = ""
    utilization_percent: float = 0.0
    memory_used_mib: float = 0.0
    memory_total_mib: float = 0.0
    temperature_c: float | None = None
    processes: list[GpuProcessInfo] = Field(default_factory=list)


class SlurmJob(BaseModel):
    """Information about a Slurm job."""

    job_id: str
    user: str = ""
    state: str = ""
    job_name: str = ""
    alloc_cpus: str = ""
    runtime: str = ""
    nodelist_or_reason: str = ""
    work_dir: str = ""


class CpuInfo(BaseModel):
    """System CPU information."""

    count: int = 0
    percent: float = 0.0


class MemoryInfo(BaseModel):
    """System memory information."""

    total_gib: float = 0.0
    used_gib: float = 0.0
    percent: float = 0.0


class SystemSnapshot(BaseModel):
    """Complete system snapshot."""

    timestamp: str = ""
    host: str = ""
    cpu: CpuInfo = Field(default_factory=CpuInfo)
    memory: MemoryInfo = Field(default_factory=MemoryInfo)
    gpus: list[GpuInfo] = Field(default_factory=list)
    processes: list[ProcessInfo] = Field(default_factory=list)
    slurm_jobs: list[SlurmJob] = Field(default_factory=list)
