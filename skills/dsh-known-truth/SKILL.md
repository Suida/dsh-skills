---
name: dsh-known-truth
description: >-
  Verified knowledge about DSH (DeepSeek Harness) internals: profile/bundle
  mechanics, composition & patch layers, and default-disabled features.
  Use when the request mentions "dsh profile", "dsh plugin", "cordis.patch.yml",
  "bundles", "创建/新建 profile", "安装 dsh 插件", "dsh 组合/补丁层",
  "启用 dsh 隐藏功能/默认关闭的功能", "dsh settings.yaml", "dsh 凭据",
  "权限预设", or debugging dsh tool-dispatch failures
  such as "Cannot read properties of undefined (reading 'prepare')".
  Covers profile creation, in-box bundle discipline, module-twin diagnosis,
  opt-in feature enabling, and official source citations.
  Do NOT use for writing Cordis plugins (use cordis-plugin-development)
  or for third-party plugin specifics.
---
# dsh Known Truth

经核实的 DSH（DeepSeek Harness）内部知识：profile/bundle 机制、组合与补丁层、
默认未启用功能。所有有源码支撑的结论均引用代码仓库（含仓内文档）出处。

## ⚠️ 版本基准（使用前必读）

本 skill 全部内容基于 **dsh CLI `0.1.0-rc.6`**（developer preview）验证。

引用任何结论前，先运行 `dsh --version` 比对：

- **一致** → 可放心引用。
- **不一致** → 必须提醒用户：「dsh-known-truth 基于 0.1.0-rc.6，与当前版本
  \<X\> 不符，结论可能已漂移」，并建议按 `references/sources.md` 中的出处
 重新核验后更新本 skill。DSH 处于 developer preview，升级常伴随协调的
 依赖与 API 变更。

## 什么时候读哪份参考

| 场景 | 阅读 |
|---|---|
| 创建/理解 profile，bundles 层顺序，bundle 解析与模板 | `references/profiles.md` |
| 工具派发崩溃（如 `reading 'prepare'`）、怀疑模块孪生、安装 in-box 包前 | `references/module-twin.md` |
| 用 `--dump-config` 验证组合、写补丁层、解析会话日志、插桩诊断 | `references/inspection.md` |
| 启用某项"默认没有"的功能（全文搜索、time-context、schedule、MCP、自省工具等） | `references/default-off-features.md` |
| settings/凭据/权限预设/agent preset/环境变量接缝 | `references/configuration-seams.md` |
| 任何结论的官方出处（SSOT 索引） | `references/sources.md` |

## 三条最承重的红线（细节见各参考文档）

1. **in-box bundle（`dsh-base` / `dsh-web-app` / `dsh-headless`）只能写在
   `dsh.profile.bundles` 数组里，绝不能 `dsh plugin add` 成依赖**——会在
   profile node_modules 制造模块孪生，首次工具派发必崩。
   健康检查：`profiles/<name>/node_modules/@deepseek-ai` 应不存在或为空。
2. **`dsh --profile <name>` 只启动不创建**；自定义 profile 的唯一创建入口是
   `dsh plugin --profile <name> add <pkg>`，且初始只有 `dsh-base`，
   表面层（web-app / headless）需手动补进 bundles。
3. **"源码里观察到可运行的行为 ≠ 受支持的接口"**——以
   `references/sources.md` 收录的官方文档/源码注释为准，未设防的路径
   不等于被允许的路径。
