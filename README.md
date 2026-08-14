# dsh-skills

[DSH（DeepSeek Harness）](https://github.com/deepseek-ai/deepseek-harness) agent
skill 集合的开发与分发主仓库。每个 skill 是一个可被 DSH 技能系统发现的
自包含目录（`SKILL.md` + 可选 `references/` 等）。

## 目录结构

```
dsh-skills/
└── skills/
    └── <skill-name>/
        ├── SKILL.md        # 必需：YAML frontmatter（name/description）+ 正文
        └── references/     # 可选：按需加载的主题文档
```

## 技能列表

| 技能 | 简介 | 版本基准 |
|---|---|---|
| [dsh-known-truth](skills/dsh-known-truth/) | 经核实的 DSH 内部知识：profile/bundle 机制、组合与补丁层、默认未启用功能、模块孪生诊断；源码级出处索引 | dsh CLI `0.1.0-rc.6` |
| [system-prompt-writing](skills/system-prompt-writing/) | system prompt 与行为规则的撰写/评审：最小规则结构、模式库、失败模式、真实案例解剖 | —（方法论，无版本依赖） |
| [dsh-skill-creator](skills/dsh-skill-creator/) | 创建、改进、评估 DSH 技能：意图捕获、description 触发写作、渐进披露、真实提示词测试、内联自我反思、打包分发 | dsh CLI `0.1.0-rc.6`（frontmatter 契约） |

## 安装与使用

DSH 从技能根目录（`$DSH_HOME/skills/`，默认 `~/.dsh/skills/`）发现技能：
`<skill-root>/<skill-name>/SKILL.md`。

**方式一：复制**（快照，之后仓库更新不会生效）

```powershell
Copy-Item -Recurse skills/dsh-known-truth ~/.dsh/skills/
```

**方式二：目录链接**（推荐，仓库即唯一事实源，git pull 即时生效）

```powershell
New-Item -ItemType Junction -Path ~/.dsh/skills/dsh-known-truth `
  -Target "$PWD/skills/dsh-known-truth"
```

安装后重启 dsh（或触发技能目录重扫）即可在会话中通过关键词触发，
或在会话中直接用 `/dsh-known-truth` 显式调用。

## 版本与维护约定

- 规范分两层：全局规范适用于所有 skill；每个有额外要求的技能在
  [AGENTS.md](AGENTS.md) 的「专项约定」下拥有自己的一节（含版本基准、
  复核方式、自查项）。
