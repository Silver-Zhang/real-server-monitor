# AGENTS.md

本仓库用于开发一个共享 Linux 科研服务器资源监控工具，命令名为 `realmon`。

该工具的目标是帮助管理员和普通用户安全、准确地查看服务器当前 CPU、内存、GPU、进程、用户、命令、工作目录以及 Slurm 作业信息。

## 一、总体原则

开发本项目时必须遵守以下原则：

1. 安全优先；
2. 只读监控；
3. 不执行任何破坏性操作；
4. 不自动修改系统配置；
5. 不要求用户配置免密 sudo；
6. 不默认暴露敏感命令行参数；
7. 普通用户权限不足时应优雅降级；
8. Slurm 或 GPU 环境不存在时程序仍应可运行；
9. 所有解析器和核心逻辑都应有测试；
10. 代码应清晰、可维护、便于以后扩展。

## 二、项目定位

本项目不是通用服务器管理平台，而是一个面向课题组共享服务器的轻量级资源监控 CLI 工具。

第一版重点：

* 当前 CPU 占用；
* 当前内存占用；
* 当前 GPU 占用；
* 每个进程对应的用户；
* 每个进程对应的命令；
* 每个进程当前工作目录；
* GPU 进程和系统进程的关联；
* Slurm 作业信息；
* JSON 输出；
* watch 刷新模式。

第一版不实现：

* Web Dashboard；
* 数据库存储；
* Prometheus exporter；
* 进程终止；
* 作业取消；
* 用户限流；
* Slurm 配置修改；
* sudoers 修改；
* 后台常驻服务。

## 三、技术栈

优先使用以下技术栈：

* Python 3.10+
* typer：命令行接口；
* rich：终端表格和格式化输出；
* psutil：CPU、内存、进程信息；
* pynvml：NVIDIA GPU 信息，可选依赖；
* pydantic：数据模型；
* pytest：单元测试。

不要引入过重的依赖。

如果新增依赖，必须说明理由，并尽量保持依赖最小化。

## 四、数据源

优先使用以下只读数据源：

* `psutil`
* `/proc/<pid>/cmdline`
* `/proc/<pid>/cwd`
* `/proc/<pid>/status`
* `/proc/<pid>/stat`
* `/proc/<pid>/cgroup`
* NVML，即 `pynvml`
* Slurm 命令：`squeue`、`scontrol`、`sacct`

可以调用的 Slurm 只读命令包括：

```bash
squeue
scontrol show job <jobid>
sacct
```

禁止调用会改变系统状态的命令，例如：

```bash
scancel
sbatch
srun
salloc
```

除非未来明确新增相应功能并经过人工审核，否则不要实现这些操作。

## 五、权限处理要求

程序必须能够在普通用户权限下运行。

如果遇到以下情况，不应崩溃：

* 无法读取其他用户的 `/proc/<pid>/cmdline`；
* 无法读取其他用户的 `/proc/<pid>/cwd`；
* Slurm 未安装；
* `squeue` 不存在；
* NVIDIA 驱动不存在；
* NVML 初始化失败；
* 当前机器没有 GPU；
* 某个进程在读取过程中已经退出。

正确行为是：

* 跳过不可读取字段；
* 保留已读取字段；
* 给出简洁提示；
* JSON 输出中使用 `null` 或空列表；
* 不打印长 traceback，除非用户显式开启 debug 模式。

## 六、隐私与脱敏要求

命令行可能包含敏感信息，必须做脱敏处理。

需要脱敏的关键词包括但不限于：

* password
* passwd
* token
* api_key
* apikey
* secret
* credential
* key

示例：

```bash
python train.py --token abcdef --password 123456
```

应显示为：

```bash
python train.py --token *** --password ***
```

也需要处理如下形式：

```bash
TOKEN=abcdef python train.py
password=123456
--api-key abcdef
--secret=abcdef
```

脱敏逻辑应集中在独立函数中，并添加单元测试。

## 七、输出字段规范

`realmon top` 默认输出列：

```text
PID | USER | CPU% | CORE_EQ | MEM_GB | GPU | GPU_MEM_MB | CWD | CMD
```

字段含义：

* `PID`：进程 ID；
* `USER`：进程所属用户；
* `CPU%`：进程 CPU 使用率；
* `CORE_EQ`：等效占用核心数，定义为 `CPU% / 100`；
* `MEM_GB`：进程 RSS 内存，单位 GiB；
* `GPU`：使用的 GPU 编号；
* `GPU_MEM_MB`：GPU 显存占用，单位 MB；
* `CWD`：进程当前工作目录；
* `CMD`：脱敏后的命令行。

默认排序：

1. GPU 显存占用高的进程优先；
2. CPU 使用率高的进程优先；
3. 内存占用高的进程优先。

需要支持：

```bash
realmon top --sort cpu
realmon top --sort mem
realmon top --sort gpu
realmon top --limit 20
```

## 八、JSON 输出规范

`realmon json` 应输出结构化 JSON，包含：

```json
{
  "timestamp": "...",
  "host": "...",
  "cpu": {},
  "memory": {},
  "gpus": [],
  "processes": [],
  "slurm_jobs": []
}
```

JSON 字段名应稳定，避免随意修改。未来其他脚本可能依赖这些字段。

如果字段无法读取，使用：

* `null`
* 空字符串
* 空列表

不要因为局部字段读取失败而导致整个 JSON 输出失败。

## 九、代码结构建议

推荐结构：

```text
src/realmon/
├── cli.py
├── models.py
├── collectors/
│   ├── procfs.py
│   ├── psutil_collector.py
│   ├── gpu_nvml.py
│   ├── slurm.py
│   └── cgroup.py
├── render/
│   ├── rich_tables.py
│   └── json_output.py
└── utils/
    ├── safe_read.py
    └── command_sanitize.py
```

设计要求：

* 数据采集逻辑放在 `collectors/`；
* 输出渲染逻辑放在 `render/`；
* 数据模型放在 `models.py`；
* 安全读取和脱敏逻辑放在 `utils/`；
* CLI 入口只负责参数解析和调度，不堆积复杂业务逻辑。

## 十、测试要求

必须为以下模块添加测试：

* Slurm 输出解析；
* 命令行脱敏；
* `/proc` 文件读取失败处理；
* NVML 不可用时的降级行为；
* JSON 输出结构；
* 排序逻辑。

测试不能依赖真实服务器环境。

不要要求测试环境必须有：

* Slurm；
* NVIDIA GPU；
* root 权限；
* 特定用户名；
* 特定服务器目录。

应使用 fixture 和 mock。

## 十一、异常处理要求

不要在普通运行模式下输出大段 traceback。

推荐行为：

* 普通用户模式：简洁错误提示；
* debug 模式：显示详细异常信息。

例如：

```bash
realmon top --debug
```

只有 debug 模式下才显示详细 traceback。

## 十二、代码风格

代码应满足：

* 类型标注尽量完整；
* 函数短小；
* 命名清晰；
* 避免过度抽象；
* 避免全局可变状态；
* I/O 与解析逻辑分离；
* 尽量使解析函数可独立测试。

不要为了第一版实现复杂架构。

## 十三、禁止事项

除非用户明确要求并经过人工审核，否则不要实现以下功能：

* kill 进程；
* scancel 作业；
* 自动提交 Slurm 作业；
* 自动修改系统文件；
* 自动修改 `/etc/sudoers`；
* 自动安装 systemd service；
* 自动开放端口；
* 无鉴权 Web 服务；
* 上传监控数据到外部服务；
* 记录完整命令行历史数据库。

## 十四、开发目标

请优先实现一个稳定、准确、安全的 MVP。

第一版完成后，应至少能够运行：

```bash
realmon top
realmon gpu
realmon slurm
realmon user zhangjunxiao
realmon json
realmon watch --interval 2
pytest
```

如果某些功能由于环境限制不可用，应优雅提示，而不是报错退出。
