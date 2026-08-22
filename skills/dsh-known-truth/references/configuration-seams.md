# 关键配置接缝

dsh 0.1.1-rc.2 出厂组合中用户可写的配置点（0.1.0-rc.6 首验，0.1.1-rc.2
复核）。组合出处：
[packages/bundle/base/cordis.patch.yml](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/base/cordis.patch.yml)。

## settings.yaml（`$DSH_HOME/settings.yaml`，热重载）

- `llm-deepseek:` 或 `llm-pi-ai:` 段**免重启**覆盖组合中对应适配器条目；
- web 的 Models 页写的就是这个文件；
- `llm-pi-ai:` 段填入 provider profiles 时路由即时注册，清空即移除；
- 0.1.1 起 `llm-pi-ai:` 支持可选 `compat` 段（route 级默认 + model 级
  逐字段覆盖：`supportsDeveloperRole` / `maxTokensField` /
  `thinkingFormat` 等），用于兼容非标 OpenAI 网关——见
  [docs/user/guide/providers.md "Request compatibility"](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/providers.md)。

## 凭据三层（`dsh-credentials-local`）

优先级：继承的环境变量 > 托管 `$DSH_HOME/.credentials.yaml` >
项目/用户 `.env` 回退。

- 适配器按 `apiKeyEnv` 引用**逐请求**解析，不物化进进程环境；
- Models 页只写托管文档；
- 0.1.1 起托管文档为 versioned 布局：`version: 1` + `refs:`（apiKeyEnv
  引用）+ `records:`（OAuth 授权记录，`<scope>/<id>`，kind:
  grant/api-key）；旧 flat 布局在 boot 时**原子自动迁移**（值逐字节
  保留；识别不了的形状响亮报错而非静默改写）；
- 注意：用户级持久环境变量（setx 设置）对**设置之前已启动**的进程
  不可见——模型路由报 `MISSING_CREDENTIAL` 时先核对进程实际继承的环境
  （实证）。

## 权限预设（`dsh-permission-presets`）

| 预设 | sandbox | approval |
|---|---|---|
| `read-only` | read-only | ask |
| `workspace-write`（默认） | workspace-write | ask |
| `danger-full-access` | danger-full-access | never |

- `DSH_PERMISSION_MODE` 环境变量控制初始值；
- approval 策略表达式：仅当模式为 `danger-full-access` 时为 `never`，
  否则 `ask`。

## agent presets

- 出厂 preset 随安装发布于应用的 `config/agent-presets/`（repo：
  [apps/cli/config/agent-presets](https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli/config/agent-presets)），
  `default: standard`；其条目带 `system` 信任、只读；
- 用户（或 agent 代写）的 preset 放 `$DSH_HOME/.agent-presets`；
- **preset 即组合**——官方注释明确其信任等级等同 shell 访问；
- web 表面下每个会话挂载一个 preset；出厂共 4 个：
  `standard` / `minimal` / `code` / `cordis`（实证，出厂 config 目录）。
  0.1.1 细节：`code` 目录 id 未变但显示名已改 **PTC 模式**；
  `minimal` 默认启用持久终端（Windows 挂 `tool-pwsh-persistent`，
  POSIX 挂 `tool-bash-persistent`）；`cordis` 默认挂 `tool-cordis`。

## 其他环境变量接缝

| 变量 | 作用 |
|---|---|
| `DSH_TOOLS_MODE` | 整个进程切入 Code Mode（`native\|code\|both`），未设为 native |
| `DSH_TELEMETRY_MODE` / `DSH_TELEMETRY_DISABLED` / `DSH_TELEMETRY_OTLP_URL` | 遥测开关与端点 |
| `DSH_HOME` | Harness home 覆盖（默认 `~/.dsh`） |
| `TZ` | time-context 省略 `timeZone` 时的进程时区回退 |
