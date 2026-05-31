# Copilot Instructions for realmon

## Project Overview
realmon is a read-only CLI tool for monitoring server resources (CPU, memory, GPU, processes, Slurm jobs) on shared Linux research servers.

## Key Principles
- **Read-only**: Never execute commands that modify system state
- **Safe**: Gracefully handle permission errors and missing dependencies
- **Privacy**: Always sanitize sensitive command-line arguments
- **No root required**: All features work as a regular user

## Architecture
- `src/realmon/cli.py` - Typer CLI entry point
- `src/realmon/models.py` - Pydantic data models
- `src/realmon/collectors/` - Data collection (psutil, /proc, NVML, Slurm)
- `src/realmon/render/` - Output rendering (rich tables, JSON)
- `src/realmon/utils/` - Utilities (safe file reading, command sanitization)

## Testing
- Run tests: `python -m pytest tests/`
- Tests use fixtures and mocks, no real GPU or Slurm needed
- All collectors must gracefully handle unavailable resources

## Dependencies
- typer, rich, psutil, pydantic (required)
- pynvml (optional, for GPU)
- pytest, pytest-mock (dev)
