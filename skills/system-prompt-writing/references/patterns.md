# 模式库

起草或改写行为规则时按需取用。每个模式给出：何时用 + 写法 + 例。

## 1. 禁止 + 理由 + 替代方案

何时用：要戒掉某个行为时。纯禁止让模型在规则未覆盖的变体前无所适从；
附带理由（为什么）和替代动作（那该怎么做），模型才能泛化。

```markdown
反例：Never use python directly.
正例：Use `uv run python` instead of bare `python` — system Python is shared
across projects, and direct calls bypass the project's locked environment.
```

## 2. 具体优于模糊（specificity beats generality）

何时用：任何规则起草时先过这一关。模糊规则的每次执行都是一次重新解读。

| 模糊（每次重新解读） | 具体（可核查） |
|---|---|
| "注意代码质量" | "提交前运行 `pnpm run typecheck`，非零退出即修复" |
| "重要变更要小心" | "删除文件或 force-push 前，先列出受影响对象并等待确认" |
| "及时处理冲突" | "我的请求与官方文档冲突时，动手前先指出并引用出处" |

## 3. 信号词加权

何时用：规则之间需要区分强度时。`MUST/ALWAYS/NEVER` 留给真正不可破的
约束；滥用会让所有规则一起贬值。普通偏好用平实语气即可——语气强度是
稀缺资源。

## 4. 负向边界

何时用：规则可能被过度套用（这是规则失效的头号路径）。显式写出"什么
情况不适用"，比指望模型自己把握分寸可靠得多。

```markdown
… Material conflicts only (correctness, security, data loss); no stylistic nits.
```

## 5. 优先级对齐

何时用：规则可能与用户的后续指令、其他规则或系统层级冲突时。写明这条
规则在层级中的位置，防止它被放大成抗命。

```markdown
… then follow the user's decision — the alert informs, it never overrides
an explicit instruction.
```

## 6. 作用域上限

何时用：默认开启的行为（不需要用户每次要求就自动发生的行为）。必须
写明豁免条件，否则它会在琐碎场景里制造噪音，最终被整体无视。

```markdown
… Skip the preview for trivial single-step tasks and pure Q&A.
```

## 7. few-shot 胜过规则堆叠

何时用：期望的输出格式或行为难以用规则描述时。给一个真实范例（输入→
输出），比再写三条规则有效。规则定义边界，范例定义形状。

## 8. 正向表述优先

何时用：能写"做什么"就不写"不做什么"。"不做 X"留下整个剩余空间供猜测；
"做 Y"指了一条路。纯粹的禁止只在替代方案显而易见时才单独成立。
