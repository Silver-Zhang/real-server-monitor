"""Tests for JSON output structure."""

import json
from unittest.mock import patch, MagicMock

from realmon.models import (
    SystemSnapshot,
    CpuInfo,
    MemoryInfo,
    GpuInfo,
    ProcessInfo,
    SlurmJob,
    GpuProcessInfo,
)
from realmon.render.json_output import render_json


def test_json_output_structure():
    """Test that JSON output contains all required fields."""
    snapshot = SystemSnapshot(
        timestamp="2024-01-01T00:00:00+00:00",
        host="testhost",
        cpu=CpuInfo(count=8, percent=45.0),
        memory=MemoryInfo(total_gib=64.0, used_gib=32.0, percent=50.0),
        gpus=[
            GpuInfo(
                id=0,
                name="NVIDIA A100",
                utilization_percent=85.0,
                memory_used_mib=40000.0,
                memory_total_mib=81920.0,
                temperature_c=72.0,
                processes=[GpuProcessInfo(pid=1234, gpu_id=0, gpu_memory_mb=39000.0)],
            )
        ],
        processes=[
            ProcessInfo(
                pid=1234,
                user="researcher",
                cpu_percent=150.0,
                core_equivalent=1.5,
                memory_gib=8.5,
                command="python train.py",
                cwd="/home/researcher/project",
                gpu_id=0,
                gpu_memory_mb=39000.0,
            )
        ],
        slurm_jobs=[
            SlurmJob(
                job_id="12345",
                user="researcher",
                state="RUNNING",
                job_name="train",
                alloc_cpus="4",
                runtime="1:00:00",
                nodelist_or_reason="node01",
            )
        ],
    )

    output = render_json(snapshot)
    data = json.loads(output)

    # Check top-level keys
    assert "timestamp" in data
    assert "host" in data
    assert "cpu" in data
    assert "memory" in data
    assert "gpus" in data
    assert "processes" in data
    assert "slurm_jobs" in data

    # Check cpu info
    assert data["cpu"]["count"] == 8
    assert data["cpu"]["percent"] == 45.0

    # Check memory info
    assert data["memory"]["total_gib"] == 64.0

    # Check GPU info
    assert len(data["gpus"]) == 1
    assert data["gpus"][0]["name"] == "NVIDIA A100"
    assert data["gpus"][0]["utilization_percent"] == 85.0

    # Check process info
    assert len(data["processes"]) == 1
    proc = data["processes"][0]
    assert proc["pid"] == 1234
    assert proc["user"] == "researcher"
    assert proc["cpu_percent"] == 150.0
    assert proc["core_equivalent"] == 1.5
    assert proc["memory_gib"] == 8.5
    assert proc["command"] == "python train.py"
    assert proc["cwd"] == "/home/researcher/project"
    assert proc["gpu_id"] == 0
    assert proc["gpu_memory_mb"] == 39000.0

    # Check slurm jobs
    assert len(data["slurm_jobs"]) == 1
    assert data["slurm_jobs"][0]["job_id"] == "12345"


def test_json_output_empty_snapshot():
    """Test JSON output with empty/default snapshot."""
    snapshot = SystemSnapshot(
        timestamp="2024-01-01T00:00:00+00:00",
        host="testhost",
    )

    output = render_json(snapshot)
    data = json.loads(output)

    assert data["gpus"] == []
    assert data["processes"] == []
    assert data["slurm_jobs"] == []
    assert "cpu" in data
    assert "memory" in data


def test_json_output_is_valid_json():
    """Test that output is valid JSON."""
    snapshot = SystemSnapshot(
        timestamp="2024-01-01T00:00:00+00:00",
        host="testhost",
    )

    output = render_json(snapshot)
    # Should not raise
    data = json.loads(output)
    assert isinstance(data, dict)
