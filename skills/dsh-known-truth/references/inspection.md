# 检视与诊断技巧

## `--dump-config` / `--dump-default-config`

离线组合配置树并退出，不启动服务：

- 输出中 `# == <来源>` 注释标注每段行来自哪一层（base、被某 bundle
  patched、profile 补丁层等）；
- `--dump-default-config` 不含用户层与 `--patch` 覆盖层。

**能力边界（实证）**：dump 只做"组合"，**不激活插件**。静态注入
（`inject`）缺失、构造期错误等只有真实启动才暴露——dump 通过不等于
能启动，能启动不等于核心链路可用（见 `module-twin.md` 的惰性故障）。

出处：[apps/cli/README.md §Profiles](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/README.md)、
[packages/boot/app-boot/README.md（renderConfigDump）](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/app-boot/README.md)

## 补丁层语法（`cordis.patch.yml`）

- 顶层 YAML 数组；元素为 id 定向补丁或 `insert` 列表；
- id 定向补丁**替换目标行的整个 `config`**（不深合并——保留的字段必须
  重述）；
- `!!js` 表达式可用：`dshHomePath('...')`、`process.env.X`、
  `ctx.<service>.<field>`（如 webserver 行的 `ctx.webStartup.port`）；
- 补丁指向不存在的 id → 仅 stderr 警告，不报错；
- **空文件或纯注释文件会抛错**（解析结果不是数组）——停用该层要写 `[]`；
- 每次启动经 `watchUserPatches` 热加载；写坏时保留上一棵好树并广播
  `hmr/config-update-failed`。

出处：[packages/boot/app-boot/README.md §Profiles 与 loadOptionalPatches](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/app-boot/README.md)

## 会话日志格式与解析

会话持久化为 `~/.dsh/sessions/<workspace>/<session-id>/session.jsonl.zstd`：

- **逐追加拼接的独立 Zstandard 帧**：一个仅含 header 行的校验帧 + 每个
  持久化追加批次一帧（官方文档明确此格式）；
- Node `zlib.zstdDecompressSync` / 流式解码默认只读出**第一帧**——
  需按帧魔数 `28 b5 2f fd` 切分后逐帧解压（实证）；
- `compression: 'none'` 时为裸 `.jsonl`。

出处：[packages/session/session-persistence-jsonl/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-persistence-jsonl/README.md)

常用事件类型（`SessionEventMap`）：`turn/start` / `turn/end`（
`reason.kind`：`completed` / `aborted` / `error` / `interrupted` /
`max-tokens`）、`step/start|end`、`user/message`、`assistant/chunk|message`、
`tool/call|result`、`request/header`（含完整 system prompt 与模型配置）。
错误 `code: "UNKNOWN"` 来自统一的错误归一化（非 HarnessError 的异常
保留原始 message、code 记为 UNKNOWN）。

## 插桩诊断通用姿势

排查"哪个副本/哪段代码在跑"类问题（实证有效流程）：

1. 先用只读手段缩小范围（会话日志、`--dump-config`、进程/文件时间戳）；
2. 在嫌疑文件加 `console.error` 探针（构造函数打 `import.meta.url`，
   关键分支打变量状态）；
3. **重启被测实例**再复现——dsh 插件进程内常驻，不重启探针不生效；
4. 结束后还原探针。
