---
name: wezterm-drive
description: >-
  用脚本控制本机正在运行的 WezTerm 终端：新建/拆分 pane、向 pane 注入命令、
  等待执行完成并取回输出与退出码、读取滚动缓冲区。Use when a request says
  "wezterm", "控制终端", "终端自动化", "在终端里跑/执行", "持久 shell 会话",
  "向终端注入命令", "长命令 转义", "spawn pane", "split pane", "wezterm cli",
  "终端里起一个 subagent / agent 会话", "dashboard 分屏", "分屏跑", "拆分终端窗口",
  "wezterm pane", "看终端里跑的结果", "读取终端输出", or asks to run something
  in a visible/persistent terminal instead of a one-shot shell.
  Covers spawn/split/send/exec(带完成探测)/read/kill 与 pane 命名寻址。
  Do NOT use for tmux/zellij 等其它 multiplexer（本 skill 只针对 WezTerm）、
  WezTerm 外观/字体/配色配置、或不需要可见终端的普通一次性命令（直接用 shell 工具即可）。
---

# wezterm-drive

通过 `scripts/wzt.py`（零依赖 Python，封装 `wezterm cli`）程序化控制 WezTerm。
前置条件：WezTerm 已安装且 GUI 正在运行（`wezterm cli` 自动连 GUI 实例，无需配置）。

## Quick start

所有命令形如 `uv run scripts\wzt.py <子命令>`——`scripts/wzt.py` 就在本 skill
目录下（DSH 加载 skill 时给出的 base directory；无 uv 时 `python ...` 亦可；
下文简写为 `wzt`）。首次在一台机器上使用先跑 `wzt doctor` 验证连通性
（输出含 wezterm 版本号，可用于版本基准比对）。

```
wzt list                        # 所有 pane（含已注册的名字）
wzt spawn --name build -- pwsh -NoLogo      # 新窗口（agents workspace），返回 {"pane_id": N}
wzt exec build "cargo test" --shell pwsh    # 注入执行，等完成，返回输出+退出码
wzt read build --lines 20                   # 读最近 20 行（含 scrollback）
wzt kill build
```

**隔离是默认行为**：`spawn` 总是新开窗口并放进 `agents` workspace（可用
`--workspace` 改名）——agent 的活动不应往用户正在使用的窗口里加 tab。
仅当用户明确要求时才用 `spawn --tab`（当前窗口开 tab）。kill 掉窗口里
最后一个 pane 时窗口随之关闭，清理就是逐个 kill 自己 spawn 的 pane。

PANE 参数一律接受 **pane-id 数字或注册名**（`--name` 注册；注册表存于本机
`%LOCALAPPDATA%\wzt`，自动清理死 pane，不随仓库同步）。
spawn 后 shell 提示符就绪需要约 1 秒——立刻 exec 通常也能工作（输入会进 pty
缓冲），但紧接着读取输出时最好留出这个余量。

## 核心工作流：在持久 pane 里跑命令并拿到结果

`exec` 是主要入口。它把命令包上开始/结束标记（`__WZT_S_<token>__` /
`__WZT_E_<token>_<code>__`）后整块粘贴注入，轮询 pane 文本直到结束标记出现，
返回 JSON：`{"ok": true, "exit_code": N, "output": "..."}`。

- `--shell pwsh|powershell|bash|sh|zsh|cmd` 必须匹配 pane 里实际运行的 shell
  （spawn 时用了什么程序就是什么 shell；默认 pwsh）。选错方言 → 标记不展开 → 超时。
- `--timeout` 默认 120s；超时返回 `{"ok": false, "timeout": true, "output_tail": ...}`，
  **命令仍在 pane 里继续跑**，之后可用 `read` 观察。
- 命令文本从 argv 或 stdin 传入，经 bracketed paste 整体进入编辑缓冲再一次性提交——
  多行脚本、引号、特殊字符都不会被外层 shell 二次转义，这是用它而非 shell 工具的理由。
- pwsh 下命令被包在 `try { } catch { }` 里，`-ErrorAction Stop` 这类终止错误也会被
  捕获并记 exit_code=1，错误文本进 output。

## 何时用 `send` + `read` 而不是 `exec`

交互式程序（REPL、TUI、ssh 会话、需要中途看输出的长任务）不能用 `exec` 等待完成：

```
wzt send build "ssh user@host"     # 注入并回车（--no-enter 可只放编辑缓冲）
wzt read build --lines 10          # 之后任意时刻观察
```

## 布局与组织

- `split --name X --right --percent 30 --pane-id P` 拆分 pane。**`--pane-id` 必填，
  且 P 必须是 agent 自己 spawn 的 pane**——默认活动 pane 属于用户，切分它会
  打乱用户的窗口布局（工具会拒绝缺省调用并解释原因）。
- 同一窗口内多 pane 并行任务的正确姿势：先 `spawn` 一个新窗口（自动进 agents
  workspace），再对它 `split` 出所需的 pane。
- `split-pane --move-pane-id` 是 wezterm 原生能力（wzt 未封装，可直接
  `wezterm cli split-pane ...`）。
- 读全量输出：`read P --all`（整个 scrollback）或 `--lines N`。

## 坑位（都是实测得出的，不要绕开）

1. **提交用 CR 不是 LF**：wzt 内部已处理；手写 `wezterm cli send-text` 时，`\n`
   不会提交命令行（PSReadLine/readline 下是插入换行），必须另发 `--no-paste "\r"`。
2. `exec` 的退出码来自 shell 的退出码变量（pwsh=`$LASTEXITCODE`，bash=`$?`）；
   pwsh 中纯 cmdlet 的非终止错误不改退出码（报 0）——需要判错时用
   `-ErrorAction Stop` 让 catch 捕获。
3. pane 里的程序退出（用户 `exit`、进程崩溃）会让 pane 消失；`exec` 此时返回
   `{"ok": false, "pane_gone": true}`，名字自动从注册表清除。
4. `exec` 期间该 pane 被占用；同一 pane 并发注入会把输入混在一起——一个 pane
   同时只跑一条命令，要并行就多 spawn 几个。
5. pane 输出中的 emoji/Unicode 正常支持（wzt 强制 UTF-8 输出）。
6. 窄 pane（如 `--percent 30` 的 split）里一切输出都会折行——刚注入的文本可能
   「藏」在视野上方几行。观察时别只取最后两三行，用 `read --lines 20` 或 `--all`。

## 底层直通

wzt 未封装的 wezterm 能力可直接调 `wezterm cli`：`set-tab-title`、`zoom-pane`、
`activate-pane`、`move-pane-to-new-tab`、`rename-workspace`、`list-clients`。
完整子命令面见 `wezterm cli --help`。
