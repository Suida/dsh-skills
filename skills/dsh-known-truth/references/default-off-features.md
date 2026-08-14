# 默认未启用的功能速查

以下功能在 dsh 0.1.0-rc.6 的出厂组合（`dsh-base` + `dsh-web-app`）中
默认关闭、休眠或未挂载。开启方式：编辑 `profiles/<name>/cordis.patch.yml`
（语法见 `inspection.md`）。组合文件出处：
[packages/bundle/base/cordis.patch.yml](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/base/cordis.patch.yml)、
[packages/bundle/web-app/cordis.patch.yml](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/web-app/cordis.patch.yml)。

## 已安装但默认关闭/休眠

| 功能 | 包 | 默认状态与开启 |
|---|---|---|
| 全文会话搜索 | `dsh-session-query-sqlite` | `openAt: never`（搜索调用报 `SESSION_QUERY_SEARCH_DISABLED`）；补丁覆盖为 `openAt: first-search`（或 `startup`）+ 持久 `path` |
| 会话遥测 | `dsh-session-telemetry-otel` | `mode` 默认 `DISABLED`；`DSH_TELEMETRY_MODE=FULL\|FEEDBACK_ONLY` 开启，`DSH_TELEMETRY_DISABLED` 彻底退出 |
| 网页抓取 | `dsh-tool-web` | `fetch: false`（fetch provider 未挂载，SSRF 防护未就绪），仅 `web_search` |
| Code Mode 工具呈现 | `dsh-tools` | 默认 `native`；`DSH_TOOLS_MODE=code\|both`（临时环境变量接缝） |
| 外部 agent 委派 | `dsh-tool-subagent` | standard preset 中有两个面向外部编码 agent 的委派 provider 行 `disabled: true`；需复制 preset 后解禁 |
| `skill-badge` | `dsh-skill-badge` | base 组合中 `disabled: true` |
| str-replace-editor | `dsh-tool-str-replace-editor` | base 挂载、web 层禁用，standard preset 未收回——web 会话实际不可用 |
| 多提供商路由 | `dsh-llm-pi-ai` | **已挂载但休眠**：零路由；settings 写入 `llm-pi-ai:` provider profiles 后动态注册（web Models 页即写该段） |
| Web 共享 HMR | `cordis-plugin-hmr` | web-app 层禁用（源码标注 TODO） |

## 已安装但未挂载（需在补丁层 insert）

| 功能 | 包 | 说明 |
|---|---|---|
| time-context | `dsh-time-context` | 每步注入当前时间/浏览器时区/耗时；混合或缺失时区来源时指示模型澄清而非猜测；`refreshIntervalMs` 节流；纯追加、KV-cache 友好。详见 [包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/context/time-context/README.md) |
| tmux-context | `dsh-tmux-context` | 告知模型其 tmux 窗格/窗口位置。[包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/context/tmux-context/README.md) |
| session-reference | `dsh-session-reference` | `ctx.sessionReferenceResolver`：其他会话的有界只读快照作为来源化上下文。[包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/context/session-reference/README.md) |
| schedule | `dsh-schedule` | agent 级持久提醒（`schedule_create/list/delete`；`at` 必须显式偏移或 `time_zone`；`every_seconds ≥ 300`；会话本地投递）。[包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/schedule/schedule/README.md) |
| 持久终端 | `dsh-terminal` / `dsh-terminal-bash` / `dsh-tool-terminal` | 跨调用保持状态的 PTY 会话。[packages/terminal](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/terminal) |
| MCP 客户端 | `dsh-mcp-client` | 每个 MCP server 一行配置；工具以 `mcp__<serverName>__<tool>` 注册。[包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-client/README.md) |
| Cordis 自省工具 | `dsh-tool-cordis` | `cordis_inspect/define/run/stop/undefine` 五工具；宿主需有 `cordis-host-runner`（web-app 已挂载）。官方信任立场：**视同 bash 权限**。[包 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/extensions/tool-cordis/README.md) |

## 仓库存在但 0.1.0-rc.6 npm 制品未包含

ACP（Agent Client Protocol）、E2B 云沙箱、LSP 集成、hooks 生命周期钩子
——见仓库 `packages/` 对应目录；安装版 CLI 的 node_modules 中不存在，
不能通过补丁层启用。

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
