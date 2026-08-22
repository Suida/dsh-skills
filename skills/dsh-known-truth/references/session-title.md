# 会话自动标题（session-title）速查

**默认启用**的子系统：三个包都在 `dsh-base` 组合行里（`cordis.patch.yml`
`id: session-title` / `id: session-title-llm`），无需任何补丁即工作。
结论基于 0.1.0-rc.6 安装版源码核对，0.1.1-rc.2 复核（默认配置值与
行为契约逐项一致）。

## 组成

| 包 | 角色 |
|---|---|
| `dsh-session-title` | 服务 `ctx.sessionTitle`：日志支撑的标题折叠、确定性 fallback、provider 注册/调度 |
| `dsh-session-title-first-prompt-llm` | 默认内置 LLM provider（`first-prompt` cadence），经 `ctx.llm` 生成 |
| `dsh-session-title-llm` | **库（非插件）**：路由解析、JSON 封帧、语言感知提示词、预算/超时/取消、流组装 |

## 流程要点

1. **触发**：`user/message`（`source.kind === 'user'` 且归一化非空）才 eligible；
   空/纯空白消息等待后续输入。首条 eligible 消息 →
   - 立即派发**确定性 fallback**：首条消息前 N 词（空白折叠、剔终端控制序列、
     按 UTF-8 字节截断、不劈码点）；
   - 仅当「全新非 fork 会话 + 恰好 1 条消息 + 尚无标题」时登记 LLM 自动修订
     （`first-prompt` 只跑一次；fork 继承标题、**永不**自动重命名）。
2. **用户改名钉住**：`rename()`（`source: user`）后不再调度自动修订；
   显式 `refresh()` 是唯一解钉方式。
3. **异步纪律**：自动 LLM 调用**绝不等主回复**；必须先等主请求的
   `request/header`（provider/model 精确 route）落日志才启动——辅助请求
   与主请求同路由（`provider`/`model` 覆盖必须成对给出，否则继承主路由）。
4. **辅助请求**：所选 human 消息 JSON 封帧，先按 `maxInputBytes` 测量（不截断）；
   派发前先追加日志事件 `session/title-llm-request`；信封
   `purpose: 'session-title'`、深冻结、无 agent-loop 进程内请求身份；
   DeepSeek 适配器对该 purpose **关闭 thinking**；只收纯文本 `stop` 输出，
   tool call / 空输出 / 非 stop 一律 reject。
5. **落盘**：校验后 `session.append("session/title", source: {kind:'provider'})`——
   纯日志事件，不开新 turn、不强制 flush（持久化在普通检查点排空）。
   折叠读取 `ctx.sessionTitle.get()` / `foldSessionTitle()` 取**最新**事件。
6. **消费**：客户端 `displayTitle` 回退链：持久化标题 → cwd basename →
   session id；冷态会话打开/恢复后 host 折叠并投影日志支撑的标题。

## 模型体验

- 标题状态对模型**不可见**：不进会话表面、`deriveMessages()`、system prompt、
  工具 schema、请求前缀；主请求 **0 token**、KV 缓存不变。
- 全新会话首条消息最多一次自动辅助调用；显式 refresh 可多次。
- 自动失败仅 warn 并保留现有标题（只能 `refresh()` 重试）；更新的修订 /
  provider 卸载 / 会话销毁 / refresh 会 abort 旧工作（`supersede` +
  AbortSignal.any），过期完成无法追加。

## 默认配置（dsh-base；可在 profile `cordis.patch.yml` 覆盖）

```yaml
session-title:                 # @deepseek-ai/dsh-session-title
  fallbackMaxWords: 5
  fallbackMaxBytes: 40
  maxTitleBytes: 80
session-title-llm:             # @deepseek-ai/dsh-session-title-first-prompt-llm
  targetWords: 5
  targetCjkCharacters: 10
  maxInputBytes: 4096
  maxOutputTokens: 64
  timeoutMs: 60000
  # provider/model: 可选显式路由，必须成对
```

## 已知边界

- provider 注册表**至多一个**实现；出厂 bundle 仍只挂 `first-prompt`。
  0.1.1 起仓内新增 `@deepseek-ai/dsh-session-title-all-prompts-llm`
  （`all-prompts` cadence：每条 eligible human 消息后重新修订标题，
  新修订 supersede 旧工作），但**未随 CLI 制品分发**、任何出厂组合
  未挂载——要用需自行安装并替换 first-prompt 行。
- 无标题删除（解钉只能 `refresh`）；fallback 有 40 字节上限，长首句
  被截断。
- 侧栏搜索（0.1.1 复核）：标题 / workspace 名的本地子串匹配 **+**
  `session-query-sqlite` 全文内容命中（带 snippet）两者合并——开启
  全文索引后内容命中可见，不再是"只匹配标题与 workspace 名"。

## 出处

- [packages/session/session-title/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-title/README.md)（服务契约 + `lib/index.js` 实现）
- [packages/session/session-title-first-prompt-llm/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-title-first-prompt-llm/README.md)
- [packages/session/session-title-llm/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-title-llm/README.md)
- [packages/bundle/base/cordis.patch.yml](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/base/cordis.patch.yml)（默认配置行）
