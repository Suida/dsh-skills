# Profile 体系

dsh 的部署单元。结论基于 dsh CLI 0.1.0-rc.6 验证，0.1.1-rc.2 复核
（所引机制文件两版间逐字节未变）。

## 目录结构

一个 profile 是 `$DSH_HOME/profiles/<name>/` 目录，包含：

- `package.json` — out-of-tree 插件 `dependencies` + profile 清单
  `dsh.profile`（含**有序** `bundles` 层列表）
- `cordis.patch.yml` — 该 profile 的用户补丁层
- `pnpm-workspace.yaml` — out-of-tree 插件的 pnpm 设置

出处：[apps/cli/README.md §Profiles](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/README.md)、
[packages/boot/app-boot/README.md §Profiles](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/app-boot/README.md)；
`pnpm-workspace.yaml` 的出处是源码
[packages/boot/app-boot/src/profile.ts](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/app-boot/src/profile.ts)
（`PROFILE_PNPM_WORKSPACE` 常量与 `initProfile` 写入）。

## 组合顺序

配置树从空根逐层合成：

1. 各 bundle 的补丁，按 `dsh.profile.bundles` 顺序
2. profile 的 `cordis.patch.yml`
3. home 级 `$DSH_HOME/cordis.patch.yml`（因此优先于 profile 层）
4. `--patch` 覆盖层

出处：[apps/cli/README.md §Profiles](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/README.md)

## 启动 ≠ 创建；模板只有 web 和 headless

- `dsh --profile <name>` 只**启动**。`web` 与 `headless` 首次使用自动按
  内置模板初始化；**任何其他名字启动即报错**：
  `profile "<name>" does not exist; create it with 'dsh plugin --profile <name> add <package>'`
- 模板内容（源码 SSOT）：
  `web = ['@deepseek-ai/dsh-base', '@deepseek-ai/dsh-web-app']`，
  `headless = ['@deepseek-ai/dsh-base', '@deepseek-ai/dsh-headless']`

出处：[apps/cli/README.md L16](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/README.md)、
[packages/boot/app-boot/src/profile.ts PROFILE_TEMPLATES 与报错处](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/app-boot/src/profile.ts)
（实证：对不存在名字启动，逐字复现该报错）

## 创建路径与初始形态

- 自定义 profile 的**唯一创建入口**是 `dsh plugin --profile <name> <pnpm args>`
  （pnpm 转发器；任何转发命令都会先初始化缺失的 profile）。
- 初始化模板写死为 `DEFAULT_PROFILE_BUNDLES = ['@deepseek-ai/dsh-base']`——
  **只有共享内核，没有任何应用表面层**。
- reconcile 机制：pnpm 操作成功后，把解析后声明了 `dsh.bundle` 的依赖自动
  追加进 bundles；被移除或失去声明的依赖自动移出。

出处：[packages/boot/app-boot/src/profile.ts](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/app-boot/src/profile.ts)、
[apps/cli/src/plugin.ts](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/src/plugin.ts)

## 三个 in-box bundle 的角色

| bundle | 角色 |
|---|---|
| `@deepseek-ai/dsh-base` | 每个 profile 先应用的内核补丁（会话、工具、沙箱、LLM……），**无表面** |
| `@deepseek-ai/dsh-web-app` | 浏览器 GUI 表面 |
| `@deepseek-ai/dsh-headless` | 一次性任务运行器 |

自定义 profile 要可用，必须手动把表面层补进 `bundles`（无 CLI 命令覆盖
此操作）。`base + web-app + headless` 三层叠加是官方形态
（`INSTALLATION_OWNED_PROFILE_TUPLES`）。

出处：[apps/cli/composition.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/composition.md)、
[packages/boot/app-boot/src/profile.ts](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/app-boot/src/profile.ts)

## bundle 的定义与解析

- bundle = manifest 声明 `"dsh": { "bundle": { "patch": "./cordis.patch.yml" } }`
  的 npm 包；`loadProfile` 对 bundles 中无此声明的包 fail loud。
- 解析**双锚点**：dsh 安装目录优先，profile 目录其次。
- `healProfilesModuleFallback` 维护 `$DSH_HOME/profiles/node_modules`
  符号链接农场（安装闭包每包一个链接），使裸包名经 Node 父目录回溯解析
  "without pnpm managing in-box packages"。

出处：[packages/boot/app-boot/README.md §Profiles](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/boot/app-boot/README.md)、
[apps/cli/README.md L39](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/README.md)

## 创建一个"与 web 相同"的自定义 profile

1. `dsh plugin --profile <name> add <任意 out-of-tree 插件>`（仅初始化时
   也可转发无害 pnpm 命令）→ 得到仅含 `dsh-base` 的 profile；
2. 手动编辑 `package.json`，把 `"@deepseek-ai/dsh-web-app"` 加进
   `dsh.profile.bundles`（在 base 之后）——保持纯 bundle 引用，**不要**
   加进 `dependencies`（原因见 `module-twin.md`）；
3. `dsh --profile <name>` 启动；web 应用自身的标志（如 `--port`）跟在
   profile 名之后。

注：官方文档未提供该流程的端到端教程，以上为文档机制的拼装。
