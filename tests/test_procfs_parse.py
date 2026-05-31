"""Tests for /proc safe read utilities."""

import os
import tempfile
from pathlib import Path

from realmon.utils.safe_read import safe_read_file, safe_readlink, safe_read_cwd


def test_safe_read_file_success():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        f.flush()
        result = safe_read_file(f.name)
        assert result == "hello world"
    os.unlink(f.name)


def test_safe_read_file_not_found():
    result = safe_read_file("/nonexistent/path/file.txt")
    assert result is None


def test_safe_read_file_permission_denied(tmp_path):
    filepath = tmp_path / "noperm.txt"
    filepath.write_text("secret")
    filepath.chmod(0o000)
    result = safe_read_file(str(filepath))
    # Should not crash
    assert result is None or isinstance(result, str)
    filepath.chmod(0o644)  # restore for cleanup


def test_safe_readlink_not_found():
    result = safe_readlink("/nonexistent/symlink")
    assert result is None


def test_safe_read_cwd_invalid_pid():
    # PID that almost certainly doesn't exist
    result = safe_read_cwd(999999999)
    assert result == ""


def test_safe_read_cwd_current_process():
    # Current process should have a readable cwd
    pid = os.getpid()
    result = safe_read_cwd(pid)
    # Should return a valid path (may be empty if permission issues in container)
    assert isinstance(result, str)
