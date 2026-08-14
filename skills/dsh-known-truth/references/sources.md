# 官方出处索引（SSOT 导航）

所有引用指向代码仓库 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)
（git 版本管理；仓内 README/文档随代码同库演进）。**不引用官网文档**
（无版本管理，无法与本 skill 的版本基准对齐）。仓库当前无 tag/release
里程碑，链接按 `master` 分支路径给出；版本漂移时以提交历史核对。

## profile / bundle / 创建机制

| 出处 | 它是什么问题的 SSOT |
|---|---|
| [apps/cli/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/README.md) | CLI 命令语法；profile 目录结构；组合层顺序；bundle 双锚点解析；"web/headless 自动初始化、其他名字经 dsh plugin 创建" |
| [packages/boot/app-boot/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/app-boot/README.md) | profile 机器全貌：bundle 定义、loadProfile 双锚点、healProfilesModuleFallback 链接农场、补丁层热加载与语法、boot/dump 语义 |
| [packages/boot/app-boot/src/profile.ts](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/app-boot/src/profile.ts) | `PROFILE_TEMPLATES` / `DEFAULT_PROFILE_BUNDLES` / `INSTALLATION_OWNED_PROFILE_TUPLES` / "profile does not exist" 报错的源码事实 |
| [apps/cli/src/plugin.ts](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/src/plugin.ts) | `dsh plugin` = pnpm 转发器 + reconcile；"In-box bundles are not dependencies" 注释 |
| [apps/cli/composition.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/composition.md) | dsh-base 全部插件行的生成式清单（"base 有什么"） |

## 组合文件（默认开关的出处）

| 出处 | 内容 |
|---|---|
| [packages/bundle/base/cordis.patch.yml](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/base/cordis.patch.yml) | 内核层全部行：全文搜索 `openAt: never`、遥测默认 DISABLED、`tool-web` fetch 关闭、权限预设、skill-badge disabled 等 |
| [packages/bundle/web-app/cordis.patch.yml](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/bundle/web-app/cordis.patch.yml) | web 表面层：host 行、浏览器插件名册、agent-plane 行移入 preset 的禁用集、`DSH_TOOLS_MODE` 接缝 |
| [apps/cli/config/agent-presets](https://github.com/deepseek-ai/deepseek-harness/tree/master/apps/cli/config/agent-presets) | 出厂 agent preset（standard 等）的 composition |

## 功能包 README（语义与限制的 SSOT）

| 主题 | 出处 |
|---|---|
| time-context | [packages/context/time-context](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/context/time-context/README.md) |
| tmux-context / session-reference / context 家族总览 | [packages/context](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/context/README.md) |
| schedule 持久提醒 | [packages/schedule/schedule](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/schedule/schedule/README.md) |
| MCP 客户端 | [packages/mcp/mcp-client](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-client/README.md) |
| Cordis 自省工具（含信任立场） | [packages/extensions/tool-cordis](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/extensions/tool-cordis/README.md) |
| 持久终端 | [packages/terminal](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/terminal) |
| 会话日志 zstd 帧格式 | [packages/session/session-persistence-jsonl](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-persistence-jsonl/README.md) |
| 会话自动标题（服务 + 默认 LLM provider + 共享库） | [packages/session/session-title](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-title/README.md) · [packages/session/session-title-first-prompt-llm](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-title-first-prompt-llm/README.md) · [packages/session/session-title-llm](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-title-llm/README.md)；默认配置行见 `packages/bundle/base/cordis.patch.yml` |
| 模块孪生所涉包 | [packages/core/tools](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/core/tools) · [packages/core/agent-loop](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/core/agent-loop) |

## 使用建议

- 回答"官方怎么说"时引用本表链接；回答"现在版本还是不是这样"时，
  先核对链接文件的最新提交。
- 本 skill 中标记「实证」的结论来自 0.1.0-rc.6 本地运行时证据
  （插桩日志、会话日志、命令实测），源码侧无直接文档；引用时说明其
  实证性质。
