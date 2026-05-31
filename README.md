# realmon

A read-only CLI tool for monitoring server CPU, memory, GPU, processes, and Slurm jobs on shared Linux research servers.

## Features

- **Process monitoring**: View top processes by CPU, memory, or GPU usage
- **GPU monitoring**: NVIDIA GPU utilization, memory, temperature, and per-process GPU memory
- **Slurm integration**: View current Slurm job queue
- **User filtering**: View resources consumed by a specific user
- **JSON output**: Machine-readable structured output
- **Watch mode**: Auto-refreshing display
- **Privacy-safe**: Sensitive command-line arguments are automatically redacted

## Installation

```bash
# Basic installation
pip install .

# With GPU support (requires NVIDIA drivers)
pip install ".[gpu]"

# Development
pip install -e ".[dev]"
```

## Requirements

- Python 3.10+
- Linux (uses `/proc` filesystem)
- Optional: NVIDIA GPU with drivers (for GPU monitoring)
- Optional: Slurm (for job queue monitoring)

## Usage

### Top processes

```bash
# Default view (GPU processes first, then by CPU, then by memory)
realmon top

# Sort by CPU usage
realmon top --sort cpu

# Sort by memory
realmon top --sort mem

# Sort by GPU memory
realmon top --sort gpu

# Limit number of processes shown
realmon top --limit 20
```

### GPU status

```bash
realmon gpu
```

### Slurm jobs

```bash
realmon slurm
```

### User processes

```bash
realmon user <username>
```

### JSON output

```bash
realmon json
```

### Watch mode

```bash
# Refresh every 2 seconds (default)
realmon watch

# Custom interval
realmon watch --interval 5
```

## Output Fields

| Field | Description |
|-------|-------------|
| PID | Process ID |
| USER | Process owner |
| CPU% | CPU usage percentage |
| CORE_EQ | Equivalent CPU cores used (CPU% / 100) |
| MEM_GB | Resident memory in GiB |
| GPU | GPU device ID (if using GPU) |
| GPU_MEM_MB | GPU memory used in MiB |
| CWD | Process working directory |
| CMD | Command line (sanitized) |

## JSON Output Structure

```json
{
  "timestamp": "2024-01-01T00:00:00+00:00",
  "host": "hostname",
  "cpu": {"count": 64, "percent": 45.0},
  "memory": {"total_gib": 256.0, "used_gib": 128.0, "percent": 50.0},
  "gpus": [...],
  "processes": [...],
  "slurm_jobs": [...]
}
```

## Slurm Integration

When Slurm is installed, `realmon slurm` displays the current job queue by parsing `squeue` output. If Slurm is not available, the command gracefully shows "Slurm not available" instead of erroring.

Only read-only Slurm commands are used (`squeue`, `scontrol show job`). No job-modifying commands (`scancel`, `srun`, `sbatch`) are ever executed.

## GPU Dependencies

GPU monitoring requires:
- NVIDIA GPU with installed drivers
- `pynvml` Python package (`pip install "realmon[gpu]"`)

If `pynvml` is not installed or NVML initialization fails, GPU features gracefully degrade and show "No GPU information available".

## Permission Limitations

This tool runs as a regular user and does **not** require root privileges.

Some limitations when running as a non-root user:
- Cannot read `/proc/<pid>/cwd` for other users' processes on some systems
- Cannot read full command lines of other users' processes on hardened systems
- Fields that cannot be read are shown as empty rather than causing errors

## Privacy & Security

- **Command sanitization**: Sensitive arguments (passwords, tokens, API keys, secrets, credentials) are automatically redacted with `***` in all output
- **Read-only**: No system modifications are ever performed
- **No network**: No data is sent anywhere
- **No root**: Does not require or use elevated privileges

## What This Tool Does NOT Do

- Web dashboard or HTTP server
- Database or historical data storage
- Prometheus metrics export
- User authentication
- Process killing or signal sending
- Slurm job cancellation or submission
- Rate limiting or resource enforcement
- System configuration changes
- Anything requiring root privileges
