# 默认未启用的功能速查

以下功能在 dsh 0.1.1-rc.2 的出厂组合（`dsh-base` + `dsh-web-app`）中
默认关闭、休眠或未挂载（0.1.0-rc.6 首验，0.1.1-rc.2 逐行复核）。开启方式：
编辑 `profiles/<name>/cordis.patch.yml`（语法见 `inspection.md`）。组合文件出处：
[packages/bundle/base/cordis.patch.yml](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/base/cordis.patch.yml)、
[packages/bundle/web-app/cordis.patch.yml](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/web-app/cordis.patch.yml)。

## 已安装但默认关闭/休眠

| 功能 | 包 | 默认状态与开启 |
|---|---|---|
| 全文会话搜索 | `dsh-session-query-sqlite` | `openAt: never`（搜索调用报 `SESSION_QUERY_SEARCH_DISABLED`）；补丁覆盖为 `openAt: first-search`（或 `startup`）+ 持久 `path` |
| 会话遥测 | `dsh-session-telemetry-otel` | `mode` 默认 `DISABLED`；`DSH_TELEMETRY_MODE=FULL\|FEEDBACK_ONLY` 开启，`DSH_TELEMETRY_DISABLED` 彻底退出 |
| 网页抓取 | `dsh-tool-web` | `fetch: false`（fetch provider 未挂载，SSRF 防护未就绪），仅 `web_search` |
| Code Mode 工具呈现 | `dsh-tools` | 默认 `native`；`DSH_TOOLS_MODE=code\|both`（临时环境变量接缝） |
| 外部 agent 委派 | `dsh-tool-subagent` | standard preset 中 Codex / Claude Code 两个委派 provider 行 `disabled: true`；0.1.1 起 provider 本体移出 base，拆为**独立发布包** `@deepseek-ai/dsh-subagent-codex` / `dsh-subagent-claude-code`。启用路径：先 `dsh plugin --profile <name> add` 对应 bundle 并**重启 Host**，再复制 preset 删掉 `disabled`（preset 内注释原话）。另注意 preset 行新写法 `backgroundMode:`（旧键 `enableRunInBackground` 仍并存兼容） |
| `skill-badge` | `dsh-skill-badge` | base 组合中 `disabled: true` |
| str-replace-editor | `dsh-tool-str-replace-editor` | base 挂载、web 层禁用，standard preset 未收回——web 会话实际不可用；但 minimal preset 已默认挂载它 |
| 多提供商路由 | `dsh-llm-pi-ai` | **已挂载但休眠**：零路由；settings 写入 `llm-pi-ai:` provider profiles 后动态注册（web Models 页即写该段） |
| Web 共享 HMR | `cordis-plugin-hmr` | web-app 层禁用（源码标注 TODO） |

## 已安装但未挂载（需在补丁层 insert）

| 功能 | 包 | 说明 |
|---|---|---|
| time-context | `dsh-time-context` | 每步注入当前时间/浏览器时区/耗时；混合或缺失时区来源时指示模型澄清而非猜测；`refreshIntervalMs` 节流；纯追加、KV-cache 友好。详见 [包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/context/time-context/README.md) |
| tmux-context | `dsh-tmux-context` | 告知模型其 tmux 窗格/窗口位置。[包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/context/tmux-context/README.md) |
| schedule | `dsh-schedule` | agent 级持久提醒（`schedule_create/list/delete`；`at` 必须显式偏移或 `time_zone`；`every_seconds ≥ 300`；会话本地投递）。[包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/schedule/schedule/README.md) |
| 持久终端 | `dsh-terminal` / `dsh-terminal-bash` / `dsh-tool-bash-persistent` / `dsh-tool-pwsh-persistent` | 跨调用保持状态的 PTY 会话。0.1.1 起 **minimal preset 已默认挂载**（Windows 挂 pwsh-persistent，POSIX 挂 bash-persistent）；standard preset 仍需手动。[packages/terminal](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/terminal) |
| MCP 客户端 | `dsh-mcp-client` | 每个 MCP server 一行配置；工具以 `mcp__<serverName>__<tool>` 注册。[包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-client/README.md) |
| Cordis 自省工具 | `dsh-tool-cordis` | `cordis_inspect/define/run/stop/undefine` 五工具；宿主需有 `cordis-host-runner`（web-app 已挂载）。0.1.1 起**出厂 cordis preset 已挂载**该工具行，其他 preset 仍需手动。官方信任立场：**视同 bash 权限**。[包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/extensions/tool-cordis/README.md) |

注：`session-reference` 曾列于本表；0.1.1 起 `dsh-web-app` 已默认挂载，
**不要**再在 profile 补丁层 insert（同 id 重复会在启动时抛
`duplicate loader entry id`）。

## 仓库存在但 0.1.1-rc.2 npm 制品未包含

ACP 宿主集成（`dsh-acp`）、E2B 云沙箱、LSP 集成、hooks 生命周期钩子
——见仓库 `packages/` 对应目录；安装版 CLI 的 node_modules 中不存在，
不能通过补丁层启用。`dsh-experimental-agent-team` 为 private 未发布。

另有一类**已发布但出厂组合不含**、按需 `dsh plugin add` 的官方包：
`@deepseek-ai/dsh-subagent-codex` / `dsh-subagent-claude-code` /
`dsh-subagent-acp` / `dsh-subagent-dsh-sdk`（外部 agent 委派）、
`dsh-web-search-exa` / `dsh-web-search-perplexity` / `dsh-web-fetch-http`
（web 搜索/抓取 provider）。

0.1.1 制品新收录（随 CLI 安装、可按上文方式启用）：`dsh-authorization`
（OAuth 授权流，凭据 `records:` 段）、`dsh-tool-pwsh-persistent` /
`dsh-tool-bash-persistent`（持久终端）、`dsh-file-reference(-local)` +
`dsh-client-ui-reference`（@ 文件/会话引用，web-app 已默认挂载）。

## 开启示例（补丁层片段）

```yaml
# 全文会话搜索
- id: session-query-sqlite
  config:
    path: !!js dshHomePath('session-index.db')
    openAt: first-search

# 挂载新行
- insert:
    - id: time-context
      name: '@deepseek-ai/dsh-time-context'
      config:
        timeZone: Asia/Shanghai
        refreshIntervalMs: 0
    - id: schedule
      name: '@deepseek-ai/dsh-schedule'
```
