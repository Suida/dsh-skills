---
name: system-prompt-writing
description: >-
  Craft and review system prompts and behavioral rules for agents
  (AGENTS.md clauses, system-prompt sections, standing agent instructions).
  Use when the request says "写 system prompt", "system prompt", "行为规则",
  "agent 指令", "prompt 规则", "加一条规则到 AGENTS.md", "优化/review 这段 prompt",
  "把某个协作偏好变成默认行为", or asks why a written rule isn't being followed.
  Covers the minimal rule structure (trigger + requirement + boundary),
  a pattern library, failure modes, worked examples, and authoritative sources.
  Do NOT use for authoring DSH skills (use skill-creator) or for dsh
  profile/bundle knowledge (use dsh-known-truth).
---
# System Prompt Writing

撰写与评审 agent 的 system prompt 与行为规则。

## 核心立场

System prompt **塑造行为，不注入知识**——模型该知道的已经知道，你写的
每一条规则都是一道行为约束，而每道约束都有"遵循成本"：越长越泛的规则，
被稳定执行的概率越低。写规则的第一性问题不是"它重不重要"，而是
"它能不能被持续执行"。

## 规则的最小结构

一条行为规则最多三行，三个成分：

1. **触发条件**——什么时候适用（具体到字面场景，不是抽象领域）；
2. **具体要求**——做什么，做到什么程度（可核查）；
3. **边界**——什么时候不适用 / 到什么程度为止。

```markdown
- When my request conflicts with established conventions, flag it BEFORE acting:
  cite the exact source and the concrete consequence, then propose the
  conventional alternative. Material conflicts only; no stylistic nits.
```

## 工作流

1. 从对话提取真实意图与失败场景（规则是为解决哪个具体问题而生的）；
2. 按最小结构起草； fragile/反复的环节从 `references/patterns.md` 选模式；
3. 用"审查清单"自查；
4. 展示草稿给用户审（不是直接写入）。

## 审查清单

- 触发条件具体吗？（"处理文档时"是反例，"当请求说'合并 PDF'"是正例）
- 要求可核查吗？（执行与否能被客观判断）
- 有边界吗？（无边界的规则必然过度触发，然后被架空）
- 与指令层级兼容吗？（规则不能静默凌驾于用户后续指令之上）
- 够短吗？（意图简单的规则超过 3 行，先删再写）

## References

- `references/patterns.md` — 模式库：起草或改写规则时查阅
- `references/failure-modes.md` — 失败模式与对策：规则没生效/引发投诉时查阅
- `references/worked-examples.md` — 两条真实规则的逐句解剖：需要范例时查阅
- `references/sources.md` — 权威出处：需要引用依据时查阅
