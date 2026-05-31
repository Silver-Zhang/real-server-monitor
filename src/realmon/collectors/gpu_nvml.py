"""Collect GPU information using NVML (pynvml)."""

from __future__ import annotations

from realmon.models import GpuInfo, GpuProcessInfo


def is_nvml_available() -> bool:
    """Check if NVML is available."""
    try:
        import pynvml  # noqa: F401
        return True
    except ImportError:
        return False


def collect_gpu_info() -> list[GpuInfo]:
    """Collect GPU information using NVML.

    Returns empty list if NVML is not available or fails.
    """
    try:
        import pynvml
    except ImportError:
        return []

    try:
        pynvml.nvmlInit()
    except Exception:
        return []

    gpus: list[GpuInfo] = []

    try:
        device_count = pynvml.nvmlDeviceGetCount()

        for i in range(device_count):
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8")

                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)

                temperature: float | None = None
                try:
                    temperature = float(
                        pynvml.nvmlDeviceGetTemperature(
                            handle, pynvml.NVML_TEMPERATURE_GPU
                        )
                    )
                except Exception:
                    pass

                processes: list[GpuProcessInfo] = []
                try:
                    compute_procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                    for proc in compute_procs:
                        processes.append(
                            GpuProcessInfo(
                                pid=proc.pid,
                                gpu_id=i,
                                gpu_memory_mb=round(
                                    (proc.usedGpuMemory or 0) / (1024 * 1024), 1
                                ),
                            )
                        )
                except Exception:
                    pass

                gpus.append(
                    GpuInfo(
                        id=i,
                        name=name,
                        utilization_percent=float(utilization.gpu),
                        memory_used_mib=round(memory.used / (1024 * 1024), 1),
                        memory_total_mib=round(memory.total / (1024 * 1024), 1),
                        temperature_c=temperature,
                        processes=processes,
                    )
                )
            except Exception:
                continue
    finally:
        try:
            pynvml.nvmlShutdown()
        except Exception:
            pass

    return gpus


def get_all_gpu_processes(gpus: list[GpuInfo]) -> list[GpuProcessInfo]:
    """Extract all GPU processes from GPU info list."""
    processes: list[GpuProcessInfo] = []
    for gpu in gpus:
        processes.extend(gpu.processes)
    return processes
