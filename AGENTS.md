# AGENTS.md — dsh-skills 仓库维护规范

本文件约束一切在本仓库中工作的 agent（与人类贡献者）。

## 仓库定位

DSH agent skill 的集合仓库。`skills/<name>/` 即发布单元，通过复制或目录
链接安装到 `$DSH_HOME/skills/` 使用。

## 技能目录惯例（硬性）

skill 目录内**只放 agent 执行所需内容**：

- ✅ `SKILL.md`（必需，文件名大小写敏感）、`references/`、`scripts/`、`assets/`
- ❌ **不放** `README.md`、`INSTALLATION.md`、`CHANGELOG.md` 等面向人类的
  辅助文档——这是主流惯例（Anthropic 官方 skills 仓库全部如此；DSH
  skill-creator 规范明确禁止）。给人看的说明一律上移到仓库级 README。

## SKILL.md 撰写纪律

- frontmatter 仅 `name` + `description`（必要时 `whenToUse`）；
  `name` 为 hyphen-case、≤64 字符，与目录同名。
- `description` 是唯一触发器：枚举**字面触发短语**（中英双语）、覆盖
  全部能力点、带 "Do NOT use for …" 负向边界。
- 正文精简（目标 <500 行），主题细节下沉到 `references/` 并在正文给出
  明确的"何时读哪份"指引；同一事实只在一处安家。

## 引用纪律

- 源码可支撑的结论：必须引用**有版本管理的代码仓库**（含仓内文档）；
  不引用无版本管理的官网页面。
- 实证结论：标注「实证」并写明验证方法（命令、插桩、日志路径）。
- 内容不出现特定第三方项目名（第三方插件、第三方 agent 产品等）；
  Cordis 为 dsh 官方维护，可提及。

## 版本基准政策

- 每个知识型 skill 在 SKILL.md 开头声明 **dsh 版本基准**（当前：
  `0.1.0-rc.6`），并指示读者用 `dsh --version` 比对。
- 本机 dsh 升级后：按该 skill 的 `references/sources.md`（或同等出处
  索引）逐条复核，更新内容后同步提升版本基准。

## 提交前验证清单

1. 每个 `SKILL.md` 以 `---` YAML 块开头，frontmatter 字段齐全；
2. 正文引用的相对路径文件全部存在；
3. `references/` 中的仓库链接可访问（抽查）；
4. 无第三方项目名残留；无应放仓库级的辅助文档混入 skill 目录。
