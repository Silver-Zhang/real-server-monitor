"""Utility for safely reading /proc and other system files."""

from __future__ import annotations

import os
from pathlib import Path


def safe_read_file(path: str | Path) -> str | None:
    """Read a file safely, returning None on any failure."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except (OSError, PermissionError, FileNotFoundError):
        return None


def safe_readlink(path: str | Path) -> str | None:
    """Read a symlink safely, returning None on any failure."""
    try:
        p = Path(path)
        target = os.readlink(p)
        return str(Path(target).resolve())
    except (OSError, PermissionError, FileNotFoundError, ValueError):
        return None


def safe_read_cwd(pid: int) -> str:
    """Read the current working directory of a process from /proc."""
    result = safe_readlink(f"/proc/{pid}/cwd")
    return result if result else ""
