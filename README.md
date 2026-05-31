# realmon

适用于共享 Linux 科研服务器的只读 CLI 资源监控工具，可查看 CPU、内存、GPU、进程及 Slurm 作业信息。

## 功能特性

- **进程监控**：按 CPU、内存或 GPU 使用率查看占用最高的进程
- **GPU 监控**：NVIDIA GPU 利用率、显存、温度及每个进程的显存占用
- **Slurm 集成**：查看当前 Slurm 作业队列
- **用户过滤**：查看指定用户的资源占用情况
- **JSON 输出**：结构化的机器可读输出
- **Watch 模式**：自动刷新的实时监控
- **隐私保护**：命令行中的敏感参数自动脱敏

## 安装

```bash
# 基础安装
pip install .

# 含 GPU 支持（需要 NVIDIA 驱动）
pip install ".[gpu]"

# 开发模式
pip install -e ".[dev]"
```

## 运行要求

- Python 3.10+
- Linux 系统（依赖 `/proc` 文件系统）
- 可选：安装了驱动的 NVIDIA GPU（用于 GPU 监控）
- 可选：Slurm（用于作业队列监控）

## 常用命令示例

### 查看占用最高的进程

```bash
# 默认视图（GPU 进程优先，然后按 CPU、内存排序）
realmon top

# 按 CPU 使用率排序
realmon top --sort cpu

# 按内存使用量排序
realmon top --sort mem

# 按 GPU 显存排序
realmon top --sort gpu

# 限制显示条数
realmon top --limit 20
```

### 查看 GPU 状态

```bash
realmon gpu
```

### 查看 Slurm 作业

```bash
realmon slurm
```

### 查看指定用户的进程

```bash
realmon user <用户名>
```

### 输出 JSON

```bash
realmon json
```

### Watch 模式（实时刷新）

```bash
# 默认每 2 秒刷新一次
realmon watch

# 自定义刷新间隔（秒）
realmon watch --interval 5
```

## 输出字段含义

| 字段 | 说明 |
|------|------|
| PID | 进程 ID |
| USER | 进程所属用户 |
| CPU% | CPU 使用率（百分比）|
| CORE_EQ | 等效占用核心数（CPU% / 100）|
| MEM_GB | 常驻内存（GiB）|
| GPU | GPU 编号（使用 GPU 时显示）|
| GPU_MEM_MB | GPU 显存占用（MiB）|
| CWD | 进程当前工作目录 |
| CMD | 命令行（已脱敏）|

## JSON 输出结构

```json
{
  "timestamp": "2024-01-01T00:00:00+00:00",
  "host": "主机名",
  "cpu": {"count": 64, "percent": 45.0},
  "memory": {"total_gib": 256.0, "used_gib": 128.0, "percent": 50.0},
  "gpus": [...],
  "processes": [...],
  "slurm_jobs": [...]
}
```

## Slurm 集成说明

安装了 Slurm 时，`realmon slurm` 通过解析 `squeue` 输出展示当前作业队列。若 Slurm 不可用，命令会优雅地提示"Slurm 不可用"而不是报错退出。

本工具只使用只读的 Slurm 命令（`squeue`、`scontrol show job`），**不会**执行任何修改系统状态的命令（`scancel`、`srun`、`sbatch` 等）。

## GPU 依赖说明

GPU 监控需要：
- 安装了驱动的 NVIDIA GPU
- Python 包 `pynvml`（`pip install "realmon[gpu]"`）

若 `pynvml` 未安装或 NVML 初始化失败，GPU 功能会优雅降级，显示"无 GPU 信息"，不会导致程序崩溃。

## 普通用户权限说明

本工具以普通用户身份运行，**不需要 root 权限**。

在非 root 用户下运行时，可能存在以下限制：
- 在部分系统上，无法读取其他用户进程的 `/proc/<pid>/cwd`
- 在加固系统上，无法读取其他用户进程的完整命令行
- 无法读取的字段将显示为空，不会引发错误

## 隐私与安全说明

- **命令脱敏**：密码、令牌、API 密钥、密钥等敏感参数在所有输出中自动替换为 `***`
- **只读工具**：不对系统做任何修改
- **无网络请求**：不向任何地址发送数据
- **无需 root**：不申请也不使用任何提权操作

## 当前不支持的功能（第一版暂不实现）

- Web 仪表盘或 HTTP 服务
- 数据库历史记录
- Prometheus 指标导出
- 用户登录系统
- 进程 kill 操作
- Slurm 作业取消或提交
- 自动限流或资源强制限制
- 系统配置修改
- 任何需要 root 权限的功能
