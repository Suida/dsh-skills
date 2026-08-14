---
name: skill-creator
description: >-
  Create, improve, and evaluate DSH agent skills (folders containing a SKILL.md
  with YAML frontmatter). Use whenever the user wants to create a new skill from
  scratch, turn a repeated workflow into a reusable skill, edit or optimize an
  existing skill, fix a skill that never triggers or triggers wrongly, write a
  skill description for better triggering, validate a SKILL.md, or package a
  skill for distribution — even if they don't say the word "skill" explicitly
  (e.g. "make this a skill", "I always do X manually, automate it", "why doesn't
  my skill fire"). Covers skill anatomy, description writing, progressive
  disclosure, testing with real prompts, self-review, and packaging.
whenToUse: >-
  The user asks to create, write, fix, improve, or package a skill; turns a
  workflow into reusable instructions; or wants to understand how DSH skills
  work and what makes a good SKILL.md.
---

# Skill Creator

Guidance for creating effective **DSH** skills and for improving them by
reflecting on what you wrote.

A skill is a modular, self-contained folder that extends the agent's
capabilities with specialized knowledge, workflows, or tools — an "onboarding
guide" for a task or domain. DSH discovers skills from the skill root
(`<skill-root>/<skill-name>/SKILL.md`, or a single `<name>.md` file). Only
`SKILL.md` counts — the file name is case-sensitive and must be exact.

## Core principles

### The description is the trigger — spend most of your effort there

The `description` in the YAML frontmatter is the **only** thing the model sees
when deciding whether to invoke the skill. DSH loads `name`, `description`,
and `whenToUse` into context up front; the body loads only after triggering.
Consequences:

- Put **all** "when to use" information in `description` — a "When to Use"
  section in the body is useless, the body is loaded too late.
- Models tend to **under-trigger** skills. Be "pushy": enumerate the **literal
  phrases** a matching request would contain, not an abstract description of the
  domain. For a PDF skill, write *"Use when a request says 'merge PDFs', 'split
  a PDF', 'rotate pages', or 'extract text from a PDF'"* — NOT *"use for PDF
  manipulation tasks"*. Both are accurate; only the first matches the words a
  user actually types.
- Cover **every** capability the skill has. If it does N things, name trigger
  phrases for all N — a description that mentions only the first triggers only
  for the first.
- Add a short **negative boundary** — a "Do NOT use for ..." naming adjacent
  cases that should not fire (prevents false triggers).
- Optional: repeat or reinforce trigger contexts in `whenToUse` for better
  discovery across the UI.

Good shape:

```yaml
description: >-
  [What it does — 1 sentence].
  Use when [primary triggers with literal phrases].
  Also use when [secondary triggers that might be missed].
  Covers [key capabilities].
  Do NOT use for [explicit exclusions].
```

### Concise is key — the context window is a shared resource

The skill competes for context with the system prompt, the conversation, other
skills' metadata, and the actual request. **Assume the agent is already
capable** — add only what it doesn't already know. Challenge every line: *does
the agent really need this, and does it justify its token cost?* Prefer a short
concrete example over a paragraph of explanation.

### Set appropriate degrees of freedom

Match how prescriptive you are to how fragile the task is. Think of the agent
walking a path: a narrow bridge with cliffs needs guardrails; an open field
doesn't.

| Freedom | When | Form |
|---|---|---|
| **High** | Many approaches valid, depends on context | Prose guidance, heuristics, checklists |
| **Medium** | Preferred pattern exists, some variation fine | Pseudocode, parameterized scripts |
| **Low** | Fragile, error-prone, must be done one exact way | Exact scripts, strict templates, "do-not-skip" verification |

The clearest low-freedom case is **fragile numeric work** — formulas, unit
conversions, aggregations — which should live in a bundled `scripts/` file
rather than trusting the model's in-head arithmetic.

### Explain the why, not just the what

Today's models have good theory of mind: when they understand *why* a step
matters, they handle the cases your instructions didn't enumerate. If you catch
yourself writing `ALWAYS` / `NEVER` in caps or building rigid scaffolding, treat
it as a yellow flag — reframe it as a short explanation of the underlying
reason. That's more robust and more humane to the reader.

Phrase instructions in the imperative, addressed to the agent that will run the
skill ("Extract the table…", "To rotate a page, …") — not narration about a user.

### Communicate with the user, not at them

Skill authors range from non-technical to expert. Read context cues and
calibrate: "workflow" or "example" are safe; "frontmatter", "schema", or
"assertion" may need a one-line gloss unless the user has signaled familiarity.
When in doubt, briefly define a term.

## Anatomy of a skill

```
skill-name/
├── SKILL.md            (required)
│   ├── YAML frontmatter   (name, description — required)
│   └── Markdown body      (instructions)
└── (optional)
    ├── scripts/        executable code for deterministic/repeated work
    ├── references/     docs loaded into context as needed (schemas, API docs, domain notes)
    └── assets/         files used in the produced output (templates, images, boilerplate)
```

**Progressive disclosure** — skills load in three levels; design for the
cheapest one that works:

1. **Metadata** (`name` + `description` [+ `whenToUse`]) — always in context.
   This is the trigger.
2. **SKILL.md body** — loaded only once the skill triggers. Keep it lean
   (aim under ~500 lines).
3. **Bundled resources** — loaded or executed only when a step needs them
   (effectively unlimited; scripts can run without being read into context).

Keep the core workflow and selection guidance in SKILL.md; push
variant-specific detail into `references/`, and link to those files with a
clear note on *when* to read each. Keep references one level deep (link them
directly from SKILL.md), and give any file over ~100 lines a short table of
contents at the top. When a skill spans several domains or variants, organize
references by variant (e.g. `references/aws.md`, `references/gcp.md`) so the
agent reads only the relevant one. Give each fact exactly one home — don't
repeat content in both SKILL.md and a reference file, or the two copies drift
apart (prefer the reference for anything detailed).

**Do not include** auxiliary docs about the skill's own creation — no
`README.md`, `INSTALLATION.md`, `CHANGELOG.md`, or notes on your process and
testing. They add clutter and confusion without helping the agent execute.
Only `name` and `description` are required in frontmatter; keep it minimal
(`whenToUse` only when it sharpens triggering).

## The workflow

Follow these in order, skipping a step only when there's a clear reason it
doesn't apply.

### 1. Understand the skill with concrete examples

Get a clear picture of how the skill will actually be used before writing
anything. Gather (or propose, then confirm) concrete example requests:
*"What should this enable? Can you give a few examples of what a user would say
to trigger it? What's the expected output?"* Ask the most important questions
first rather than overwhelming the user; avoid asking many questions in a
single message. Conclude once the intended functionality is clear.

If the current conversation already contains the workflow the user wants to
capture ("turn this into a skill"), extract answers from the conversation
history first — the tools used, the sequence of steps, corrections the user
made, input/output formats observed — and only fill gaps with questions.

### 2. Discover existing skills — update over create

Before scaffolding anything new, check whether a similar skill already exists
in the skill root. A near-duplicate is harmful: when two skills cover the same
ground, the agent can't tell which to invoke (triggering gets diluted), and the
same knowledge drifts out of sync across both.

List the skill root and skim each `SKILL.md`'s `name` and `description`:

- If a listed skill is **the same capability**, **update it in place** — keep
  its `name` and folder, extend its SKILL.md / resources to cover the new need,
  and **add the new need's trigger phrases to the description** (broaden it,
  never narrow): a consolidated skill must still trigger on everything its
  merged parts would have, or the consolidation silently loses coverage.
  Then continue to step 6.
- If matches are merely adjacent (related but a genuinely different
  capability), proceed to create a new one.

Use judgment: "same capability, broader scope" → update. "Shares keywords but a
different job" → new skill.

### 3. Plan reusable contents

For each concrete example, ask: how would the agent do this from scratch, and
what would help if it had to do it repeatedly? **Bundle resources generously —
a skill that adds only prose often fails to beat the baseline.** This surfaces:

- **`scripts/` — executable code for anything fragile, multi-step, or done one
  exact way. The highest-value resource, and the most under-used.** In
  particular, **work that has to be exact belongs in a script, not in prose** —
  a calculation or formula, a unit/format/date conversion, a multi-step parse
  or aggregation: anything where a model doing it in its head drifts or
  silently picks the wrong convention. Write it to take the inputs and return
  the result (e.g. `scripts/compute.py --inputs ...`), and **test it on a
  worked example with a known answer before shipping**.
- **`references/` — the exact specs the agent (and any script) must agree on**:
  the precise definition or convention a task hinges on (which formula variant,
  rounding rule, boundary, or edge-case handling), schemas, domain rules. Keep
  the authoritative version here, not paraphrased in prose.
- **`assets/`** — templates, boilerplate, images, fonts used verbatim in the
  output.

**Handle conventions explicitly.** Many exact operations have more than one
accepted convention — a formula variant, a rounding or tie-breaking rule, a
sort order, a date/boundary convention — and a request often names the one it
wants. Don't hardcode a single convention: make it a **parameter** the script
accepts (covering the common variants), **catalog the variants in
`references/`** with how to recognize which one a request is asking for, and
have the **SKILL.md detect the requested convention and pass it to the script**.

If a skill performs an exact operation and ships no script for it, treat it as
a yellow flag — the agent will re-derive it, and can mis-derive it, every run.

### 4. Scaffold (new skills only)

Create the folder and a SKILL.md skeleton under the skill root — that's all
scaffolding is. Name the folder exactly after the skill name. Only create the
resource directories you intend to populate; delete placeholders you don't need.

### 5. Write the SKILL.md and resources

Build the resources first (and test any scripts by actually running them — a
representative sample is enough when there are many similar ones), then write
the body that ties them together. Remember you're writing for another agent
instance: include the non-obvious procedural knowledge, and skip what a capable
agent already knows.

**Frontmatter** (`name`, `description`):

- `name` — hyphen-case, lowercase letters/digits/hyphens, ≤64 chars; name the
  folder to match. Prefer a short, verb-led phrase that names the action (e.g.
  `rotate-pdf`, `summarize-thread`), and namespace by tool when it sharpens
  triggering (e.g. `gh-address-comments`).
- `description` — the **primary trigger**; write it per the Core principles
  above: literal trigger phrases, every capability covered, negative boundary,
  slightly pushy. This is where completeness of concrete trigger cues beats
  elegance.
- `whenToUse` (optional) — a short restatement of trigger contexts for
  discovery surfaces that show it separately from `description`.

**Body** — instructions for using the skill and its bundled resources, written
per the Core principles above. Use these structure patterns as a starting
point, combining as fits:

- `## Quick start` (fastest safe path)
- `## When to use` / `## Decision tree` (only if it adds beyond the description)
- `## Workflows` (numbered steps; include verification loops where output is checkable)
- `## Examples` (input → output, few-shot)
- `## References` (what to open when — with explicit read cues)

### 6. Validate

Confirm by hand that:

- SKILL.md opens with a `---` YAML block; `name` is hyphen-case ≤64 chars;
  `description` is non-empty and concrete (pass the "literal phrases" test from
  step 5).
- Every file referenced in the body actually exists (scripts, references,
  assets) with correct relative paths.
- Any bundled script runs and produces the expected output on a worked example.

Fix anything that fails before presenting the skill.

### 7. Self-reflect and optimize

This step turns a first draft into a good skill. Do it **inline, yourself** —
no subagents, no separate processes. After drafting, re-read your own skill
with fresh eyes and the deliberate mindset of a skeptical reviewer who has
never seen it, then revise. Work through these lenses, and explain to yourself
*why* each change helps rather than rubber-stamping:

1. **Triggering (fresh eyes) — usually the highest-leverage fix.** Reading
   *only* the `description`, write down 3 realistic requests that *should*
   invoke this skill and 2 near-misses that should *not*. Then check two
   things: (a) does the description contain the **literal words** those
   should-trigger requests use, not just an abstract description of them? If a
   request says "rotate the PDF 90 degrees" but the description only says
   "document tasks", it will miss — add the exact phrase. (b) Does it name
   trigger cues for **every** capability in the body? Walk the body's sections
   and confirm each has a matching cue in the description. Rewrite any abstract
   framing into concrete, quoted enumerations, and add/tighten a "Do NOT use
   for ..." line if a near-miss would fire. Re-check.
2. **Self-containment.** Read the body as a fresh agent with no prior context.
   Is every instruction actionable? Any unexplained assumption, dangling
   reference to a file that isn't there, or step where you'd stall? Fix it.
3. **Concision and altitude.** Cut anything a capable agent already knows or
   that doesn't earn its tokens. Replace any all-caps MUST/NEVER with a short
   explanation of the underlying reason. Delete rules that only make sense for
   the one example you had in mind.
4. **Progressive disclosure.** Is SKILL.md carrying detail that belongs in a
   `references/` file? Move it, and leave a clear pointer about when to read
   it. Is the body over ~500 lines?
5. **Degrees of freedom.** Does the specificity match each task's fragility —
   guardrails where the operation is fragile, room to maneuver where many paths
   are valid?
6. **Dry run — and for anything numeric, actually compute it.** Mentally
   execute the skill end-to-end on one realistic request; note wherever it
   stalls, loops, or produces the wrong shape of output. If the skill computes
   a number, don't eyeball the prose math — **run its bundled script (or the
   formula) on a worked example with known inputs and confirm the result is
   exactly right.** Prose math that "looks correct" is the most common silent
   failure; a skill that describes a multi-step calculation without a script is
   the signal to write one and verify it here.

Apply the revisions. If the pass turned up substantial issues, do it once more.

### 8. Test with real prompts

After drafting (and after each meaningful revision), come up with **2–3
realistic test prompts** — the kind of thing a real user would actually say,
not carefully constructed inputs. Share them with the user: "Here are a few
test cases I'd like to try. Do these look right, or do you want to add more?"

Run each prompt against the skill yourself, one at a time, and present the
output inline for the user to judge:

- Did the skill **trigger correctly** from the test prompt?
- Did the instructions get **followed**?
- Is the **output quality** acceptable?
- Does it handle **edge cases** (missing inputs, ambiguous requests)?

Show the user the actual output and ask for feedback ("How does this look?
Anything you'd change?"). If the user provides an example or correction, run it
immediately rather than waiting for a full specification — seeing what the
agent actually does is the fastest way to refine requirements.

If the user wants a more rigorous comparison (e.g. "is the new version actually
better?"), you may optionally run the same prompt **without** the skill (or
with the previous version) and present a side-by-side comparison in the
conversation for the user to judge. This is optional and most users won't need
it — the human review loop is usually sufficient.

### 9. Iterate on real usage

Use the skill on real tasks and watch where it struggles or wastes effort.
If several runs all independently write the same helper script or take the same
multi-step detour, that's a strong signal to bundle that script (or fold that
guidance) into the skill so future runs don't reinvent it. Update SKILL.md or
its resources and repeat.

Keep going until the user says they're happy, feedback comes back clean, or
you're not making meaningful progress.

### 10. Package and present

Once the skill is finalized:

1. Verify the structure — SKILL.md exists with valid YAML frontmatter; all file
   references resolve.
2. If the user wants to distribute it, package the skill folder (the folder
   containing SKILL.md and related files) into a zip archive preserving the
   internal structure, named `<skill-name>.skill` (a zip with a `.skill`
   extension). If packaging by hand isn't available, tell the user where the
   folder is so they can copy it.
3. Tell the user where the skill lives, what it does, and how to install it
   (copy the folder under the DSH skill root, or drop the `.skill` archive in
   the right place per DSH's skill discovery rules).

## What not to include

A skill should contain only what an agent needs to do the job. Don't add
auxiliary docs about the skill's own creation — no `README.md`,
`INSTALLATION.md`, `CHANGELOG.md`, or notes on your process and testing. They
add clutter and confusion without helping the agent execute.

## Principle of no surprise

Skills must not contain malware, exploit code, or anything that could
compromise security, and a skill's behavior should not surprise the user given
its description. Don't build skills designed to mislead or to enable
unauthorized access or data exfiltration. (Benign role-play or persona skills
are fine.)

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| Skill never triggers | Make the description more explicit and "pushy" — list more literal trigger phrases |
| Skill triggers on wrong requests | Add exclusions to the description ("Do NOT use for...") |
| Agent ignores instructions | Add examples showing the desired behavior — few-shot > rules |
| Output format is inconsistent | Provide an explicit template with exact structure |
| SKILL.md is too long | Move detailed content to `references/` files with clear pointers |
| Skill is too rigid | Replace MUST/NEVER rules with explanations of WHY |
| Skill only works for test examples | Generalize from specific feedback — explain principles, not just fixes |
| Agent wastes time on unproductive steps | Read the execution transcript, remove instructions causing wasted effort |
| Exact work has no script | Write a script and test it on a worked example — the agent will mis-derive it otherwise |

## Quick reference: SKILL.md template

```yaml
---
name: your-skill-name
description: >-
  [What it does — 1 sentence]. Use when [literal trigger phrases]. Also use when
  [secondary triggers]. Covers [all capabilities]. Do NOT use for [exclusions].
---
# Your Skill Name

Brief description of what this skill does.

## Quick start
Fastest safe path.

## Workflows
Numbered steps with verification loops.

## Examples
Input → output, few-shot.

## References
- `references/xxx.md` — read when ...
```

Good luck!
