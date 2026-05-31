"""Collect process information using psutil."""

from __future__ import annotations

import datetime
import psutil

from realmon.models import ProcessInfo, CpuInfo, MemoryInfo
from realmon.utils.safe_read import safe_read_cwd
from realmon.utils.command_sanitize import sanitize_command


def collect_cpu_info() -> CpuInfo:
    """Collect system CPU information."""
    return CpuInfo(
        count=psutil.cpu_count() or 0,
        percent=psutil.cpu_percent(interval=0.1),
    )


def collect_memory_info() -> MemoryInfo:
    """Collect system memory information."""
    mem = psutil.virtual_memory()
    return MemoryInfo(
        total_gib=round(mem.total / (1024**3), 2),
        used_gib=round(mem.used / (1024**3), 2),
        percent=mem.percent,
    )


def collect_processes() -> list[ProcessInfo]:
    """Collect information about all running processes."""
    processes: list[ProcessInfo] = []

    for proc in psutil.process_iter(
        ["pid", "username", "cpu_percent", "memory_info", "cmdline", "name", "create_time"]
    ):
        try:
            info = proc.info  # type: ignore[attr-defined]
            pid = info.get("pid", 0)
            username = info.get("username") or ""
            cpu_pct = info.get("cpu_percent") or 0.0
            mem_info = info.get("memory_info")
            mem_gib = round(mem_info.rss / (1024**3), 3) if mem_info else 0.0
            cmdline = info.get("cmdline") or []
            cmd_str = " ".join(cmdline) if cmdline else (info.get("name") or "")
            cmd_str = sanitize_command(cmd_str)
            name = info.get("name") or ""
            cwd = safe_read_cwd(pid)

            start_time = None
            create_time = info.get("create_time")
            if create_time:
                try:
                    start_time = datetime.datetime.fromtimestamp(
                        create_time, tz=datetime.timezone.utc
                    ).isoformat()
                except (OSError, ValueError):
                    pass

            processes.append(
                ProcessInfo(
                    pid=pid,
                    user=username,
                    cpu_percent=round(cpu_pct, 1),
                    core_equivalent=round(cpu_pct / 100.0, 2),
                    memory_gib=mem_gib,
                    command=cmd_str,
                    name=name,
                    cwd=cwd,
                    start_time=start_time,
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return processes
