"""Tests for GPU NVML collector graceful degradation."""

import sys
from unittest.mock import patch, MagicMock

from realmon.collectors.gpu_nvml import collect_gpu_info, is_nvml_available, get_all_gpu_processes
from realmon.models import GpuInfo, GpuProcessInfo


def test_nvml_not_available_when_not_installed():
    """Test that missing pynvml doesn't crash."""
    with patch.dict(sys.modules, {"pynvml": None}):
        # Force reimport
        result = collect_gpu_info()
        # Should return empty list, not crash
        assert result == [] or isinstance(result, list)


def test_collect_gpu_info_import_error():
    """Test graceful degradation when pynvml import fails."""
    with patch("builtins.__import__", side_effect=ImportError("No module named 'pynvml'")):
        result = collect_gpu_info()
        assert result == []


def test_collect_gpu_info_nvml_init_failure():
    """Test graceful degradation when nvmlInit fails."""
    mock_pynvml = MagicMock()
    mock_pynvml.nvmlInit.side_effect = Exception("NVML init failed")

    with patch.dict(sys.modules, {"pynvml": mock_pynvml}):
        result = collect_gpu_info()
        assert result == []


def test_get_all_gpu_processes():
    """Test extracting GPU processes from GPU info."""
    gpus = [
        GpuInfo(
            id=0,
            name="GPU 0",
            processes=[
                GpuProcessInfo(pid=100, gpu_id=0, gpu_memory_mb=1024.0),
                GpuProcessInfo(pid=101, gpu_id=0, gpu_memory_mb=2048.0),
            ],
        ),
        GpuInfo(
            id=1,
            name="GPU 1",
            processes=[
                GpuProcessInfo(pid=200, gpu_id=1, gpu_memory_mb=512.0),
            ],
        ),
    ]

    procs = get_all_gpu_processes(gpus)
    assert len(procs) == 3
    assert procs[0].pid == 100
    assert procs[2].gpu_id == 1


def test_get_all_gpu_processes_empty():
    """Test with no GPU processes."""
    gpus = [GpuInfo(id=0, name="GPU 0")]
    procs = get_all_gpu_processes(gpus)
    assert procs == []
