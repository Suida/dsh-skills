# 案例解剖

两条在真实协作中打磨过的规则，逐句标注设计决策对应的模式
（编号见 `patterns.md`）。

## 案例一：Conflict alerts

```markdown
- When my request conflicts with established conventions, official
  documentation, or this file's own rules, flag it BEFORE acting: cite the
  exact source (file/section/link) and the concrete consequence, then propose
  the conventional alternative.
- The alert informs, never overrides — after I acknowledge, follow my decision
  without re-litigating. Material conflicts only (correctness, security, data
  loss, convention drift); no stylistic nits.
```

| 成分 | 设计决策 |
|---|---|
| "When my request conflicts with …" | 触发条件具体化（模式 2）：列了三类可判定的冲突对象，而非"注意各种问题" |
| "flag it BEFORE acting" | 时序约束——该规则的最大价值在动手前；事后提醒等于没提醒 |
| "cite the exact source … never a bare 'best practice says so'" | 证据形态要求（模式 2）：防止"我觉得惯例如此"式的空泛提醒 |
| "propose the conventional alternative" | 禁止+替代（模式 1）：不只否定，给路 |
| "The alert informs, never overrides" | 优先级对齐（模式 5）：规则明确自己低于用户当轮指令 |
| "after I acknowledge, follow my decision without re-litigating" | 防纠缠：提醒一次的义务，不是反复劝谏的权力 |
| "Material conflicts only … no stylistic nits" | 负向边界（模式 4）：没有这个，规则会退化成挑刺噪音 |

演变记录：初版九行（含动机段落与分步编号），被用户以"3 行就是极限"
纠正为现版——**意图简单的规则，篇幅本身就是缺陷**。

## 案例二：Plan preview

```markdown
- Before starting non-trivial work (multi-step, multi-file, or
  state-changing), post a brief execution outline first: 3–7 bullets on what
  I'll do, in what order, and where the choice points are — not a formal
  plan-mode document.
- Default show-and-go: proceed after posting. Wait for my answer only when
  the work is destructive/irreversible or a material choice is genuinely mine
  to make.
- Skip the preview for trivial single-step tasks and pure Q&A.
```

| 成分 | 设计决策 |
|---|---|
| "non-trivial work (multi-step, multi-file, or state-changing)" | 触发条件的客观判据（模式 2） |
| "3–7 bullets … not a formal plan-mode document" | 用数量上限 + 显式排除定义产出形状，防止滑向重型方案文档 |
| "Default show-and-go" | 默认行为命名：展示即走，不打断节奏 |
| "Wait … only when destructive/irreversible or a material choice is genuinely mine" | 等待批准的例外枚举——把"何时停"的判断从感觉变成清单 |
| "Skip … trivial single-step tasks and pure Q&A" | 作用域上限（模式 6）：没有它，每条问答前都贴大纲，规则必被架空 |

## 从案例中可复用的动作

- 每条规则写完后问：触发具体吗？要求可核查吗？有边界吗？层级兼容吗？
  够短吗？（即 SKILL.md 的审查清单）
- 给用户看草稿而不是直接写入——规则是长期的，审查成本是一次性的。
