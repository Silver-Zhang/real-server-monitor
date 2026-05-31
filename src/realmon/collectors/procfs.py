"""Collect process information directly from /proc filesystem."""

from __future__ import annotations

from realmon.utils.safe_read import safe_read_file, safe_read_cwd


def read_proc_cmdline(pid: int) -> str | None:
    """Read command line from /proc/<pid>/cmdline."""
    content = safe_read_file(f"/proc/{pid}/cmdline")
    if content is None:
        return None
    # cmdline is null-separated
    return content.replace("\x00", " ").strip()


def read_proc_status(pid: int) -> dict[str, str]:
    """Read and parse /proc/<pid>/status into a dict."""
    content = safe_read_file(f"/proc/{pid}/status")
    if content is None:
        return {}
    result: dict[str, str] = {}
    for line in content.splitlines():
        parts = line.split(":", 1)
        if len(parts) == 2:
            result[parts[0].strip()] = parts[1].strip()
    return result


def read_proc_cwd(pid: int) -> str:
    """Read current working directory from /proc/<pid>/cwd."""
    return safe_read_cwd(pid)
