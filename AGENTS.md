# AGENTS.md — dsh-skills 仓库维护规范

本文件约束一切在本仓库中工作的 agent（与人类贡献者）。

规范分两层：**全局规范**对所有 skill 成立；**专项约定**按技能分节，条款
仅约束对应技能且优先于全局。新技能如需额外规范，在「专项约定」下新增
一节——不得把单一技能的规则写进全局。

## 仓库定位

DSH agent skill 的集合仓库。`skills/<name>/` 即发布单元，通过复制或目录
链接安装到 `$DSH_HOME/skills/` 使用。

## 全局规范

### 技能目录惯例（硬性）

skill 目录内**只放 agent 执行所需内容**：

- ✅ `SKILL.md`（必需，文件名大小写敏感）、`references/`、`scripts/`、`assets/`
- ❌ **不放** `README.md`、`INSTALLATION.md`、`CHANGELOG.md` 等面向人类的
  辅助文档——这是主流惯例（Anthropic 官方 skills 仓库全部如此；DSH
  skill-creator 规范明确禁止）。给人看的说明一律上移到仓库级 README。

### 工作流程

- **先审后写**：新建或大改 skill 前，先把拟收录的知识/内容清单列举出来
  交用户审查，获批后再动笔；不跳过审查直接成稿。

### SKILL.md 撰写纪律

- frontmatter 仅 `name` + `description`（必要时 `whenToUse`）；
  `name` 为 hyphen-case、≤64 字符，与目录同名。
- `description` 是唯一触发器：枚举**字面触发短语**（中英双语）、覆盖
  全部能力点、带 "Do NOT use for …" 负向边界。
- 正文精简（目标 <500 行），主题细节下沉到 `references/` 并在正文给出
  明确的"何时读哪份"指引；同一事实只在一处安家。
- **单条规则级别同样从简**：意图简单的规则 3 行为限——触发条件 +
  要求 + 边界，不附带动机解释与分步编号；模型对简洁指令的遵循度更高。

### 版本依赖

技能若依赖外部版本（dsh、运行时、第三方 API 等），在其专项约定中声明
版本基准与复核方式，不写进全局。

## 专项约定

### dsh-known-truth

适用于 `skills/dsh-known-truth/`：

- **内容定位**：经核实的 DSH 内部知识参考。只收录三类可溯源结论——
  官方仓内文档、官方源码（常量/注释/组合文件）、实证（标注「实证」并
  写明验证方法）。不收推测、二手转述、无版本管理的网页内容。
- **结构**：`SKILL.md` 只承载版本基准声明、三条最承重的红线、
  references 导航表；知识本体按主题拆分 `references/`，一主题一文件。
  新增主题 = 新增文件 + 导航表加一行，不向既有文件堆叠无关内容。
- **引用纪律**：源码可支撑的结论必须引用有版本管理的代码仓库（含仓内
  文档），不引用无版本管理的官网页面；引用前确认来源权威——官方文档/
  官方源码优先，低星个人仓库与作者背景不明的博客不得作为依据；一律
  使用 `github.com/deepseek-ai/deepseek-harness` 的 blob/tree 链接，行级
  结论附 `#L` 锚点；仓库无 tag，按 `master` 路径，漂移核对方式在
  `references/sources.md` 说明。
- **内容不出现特定第三方项目名**（第三方插件、第三方 agent 产品等）；
  Cordis 为 dsh 官方维护，可提及。
- **版本基准**：当前 `0.1.0-rc.6`（SKILL.md 开头与本处保持同步），
  SKILL.md 指示读者用 `dsh --version` 比对。dsh 升级后按
  `references/sources.md` 逐条复核：内容变化则更新并提升基准；复核无
  变化也更新基准版本号（表示"已在此版本验证"）。
- **专项自查**：引用链接可访问且来源权威；无第三方项目名残留；
  基准版本号与 SKILL.md 一致。

### wezterm-drive

适用于 `skills/wezterm-drive/`：

- **版本基准**：已验证 wezterm `20240203-110809`（stable）与
  `20260823-230148`（nightly），双端（CASSY / DESKTOP-NE8T66I，后者
  `20260716-195552`）实测通过。wezterm 升级后必须复核：先
  `scripts/wzt.py doctor`（输出含版本号），再跑 exec 冒烟矩阵——
  pwsh 与 bash 各一条「成功 + 非零退出码」用例；行为变化则修
  `scripts/wzt.py` 并更新本基准。
- **专项自查**：`scripts/wzt.py` 保持零依赖（仅用 stdlib），PEP 723
  头不声明任何 dependencies；机器本地状态只写 `%LOCALAPPDATA%\wzt`
  （或 `WZT_STATE_DIR`），不得写回仓库。

## 提交前验证清单（通用）

1. 每个 `SKILL.md` 以 `---` YAML 块开头，frontmatter 字段齐全；
2. 正文引用的相对路径文件全部存在；
3. 无应放仓库级的辅助文档混入 skill 目录；
4. 新增规则符合 3 行篇幅纪律；本次内容已经过用户清单审查；
5. 涉及的技能附带其专项约定中的自查项。
