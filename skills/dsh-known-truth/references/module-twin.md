# in-box bundle 纪律与模块孪生陷阱

本主题 knowledge 来自一次真实事故的诊断（dsh 0.1.0-rc.6，插桩实证）。
标记「实证」的结论以本地运行时证据为依据；机制所涉包：
[@deepseek-ai/dsh-tools（packages/core/tools）](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/core/tools)、
[@deepseek-ai/dsh-agent-loop（packages/core/agent-loop）](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/core/agent-loop)。

## 红线

in-box bundle（`dsh-base` / `dsh-web-app` / `dsh-headless`）**只能写在
`dsh.profile.bundles` 数组里，绝不能 `dsh plugin add` 成 npm 依赖**。

源码侧的官方表述："In-box bundles from the profile template are **not
dependencies** and are never touched." —
[apps/cli/src/plugin.ts](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/src/plugin.ts)

注意：`dsh plugin add` 对此**不设防**——in-box 包声明了 `dsh.bundle`，
reconcile 会像对待普通插件一样把它收进 bundles，安装"看起来成功"。
**不报错 ≠ 被允许。**

## 故障机制（实证）

把 in-box 包装成依赖后，pnpm 会将其依赖闭包（两百余个 `@deepseek-ai/*`
包）物化到 `profiles/<name>/node_modules`，形成**部分阴影化**：

1. 闭包内的包（如 `dsh-tools`）被 profile 副本阴影；
2. 闭包外的包（如 `dsh-agent-loop`）穿过 `$DSH_HOME/profiles/node_modules`
   回退链接农场，仍解析到安装目录副本；
3. 同一包出现两个模块实例后，**模块局部 `Symbol()` 不再相等**——
   `dsh-tools` 用 `Symbol("@deepseek-ai/dsh-tools.scheduler")`（非
   `Symbol.for`）把执行调度器挂到注册表实例上，`dsh-agent-loop` 持有
   另一副本的同名符号去查找，得到 `undefined`；
4. 首次工具派发即抛
   `Cannot read properties of undefined (reading 'prepare')`，
   turn 以 `code: "UNKNOWN"` 结束。

## 关键特征

- **惰性**：启动、`--dump-config`、页面加载、纯文本对话全部正常；
  第一次工具调用才崩（与调用哪个工具无关）。
- **必然**：由安装方式决定的静态拓扑，同时序/网络无关；同一路径安装
  必然重现。反直觉推论：若闭包"全量阴影"反而可能自洽——真正的危险
  条件是**部分阴影**。

## 健康检查

```powershell
# 应不存在或为空；存在任何包即说明有阴影化风险
Get-ChildItem "$env:USERPROFILE\.dsh\profiles\<name>\node_modules\@deepseek-ai"
```

第三方插件若把 `@deepseek-ai/*` 运行时包声明为普通 dependencies（而非
peerDependencies），装进任何 profile 都会制造同款孪生。

## 诊断方法（实证有效）

1. 从会话日志取错误文本（见 `inspection.md` 的 zstd 帧解析法）；
2. 在可疑类的构造函数加 `console.error(import.meta.url)`，确认实例来自
   哪个副本；
3. 在符号查找点打印 `Object.getOwnPropertySymbols(instance)` 与
   `symbol in instance`——同名符号存在但 `in` 为 false 即模块孪生铁证；
4. 注意插桩写法：`undefined.prepare` 是**同步**抛出的，`.catch()` 链
   捕获不到，必须用 `try/catch` 包裹整个求值表达式。

## 修复

`dsh plugin --profile <name> remove <in-box 包>`（reconcile 会把它移出
bundles），再手动把包名以纯引用形式加回 `bundles` 数组。
