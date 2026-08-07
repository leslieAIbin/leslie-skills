---
name: leslie-task-contract
description: Turn vague, complex, long-running, or risky work into a portable task contract with a concrete outcome, verification evidence, constraints, write boundaries, bounded iteration, completion criteria, and pause conditions. Use whenever Leslie asks to define a goal, 写目标、整理需求、拆清验收条件、生成 /goal、让 Claude/Codex/OpenCode 持续完成任务，or when an agent task would otherwise be ambiguous or unbounded. Produce a cross-agent contract by default and add a Codex `/goal` adapter only when requested or clearly useful.
---

# Leslie Task Contract

把模糊任务收敛成 Claude Code、Codex 和 OpenCode 都能执行、验证、停止和暂停的任务契约。

## Operating rules

- Draft the contract; do not execute the contracted work unless the user also asks to execute it.
- Describe an observable outcome rather than a list of activities.
- Prefer project-provided commands and runtime evidence over invented checks.
- Infer low-risk details and disclose them under `Assumptions`; ask only when a choice changes cost, risk, ownership, or product direction.
- For unfamiliar domains, make the first phase evidence discovery from project files, official documentation, runtime state, or user-provided material.
- Bound iteration. Repeated retries without new evidence are not progress.
- Protect unrelated files, secrets, production data, default branches, external accounts, and paid services.
- Keep the portable contract tool-neutral. Add platform syntax as a separate adapter.

## Workflow

1. Restate the request as one concrete outcome.
2. Classify risk:
   - low: local drafts, prototypes, isolated scripts, non-destructive formatting;
   - medium: existing repository changes, migrations in development, shared configuration, external test APIs;
   - high: production, credentials, payments, private data, destructive deletion, regulated decisions, public publishing.
3. Inspect the supplied context for existing commands, conventions and boundaries. Do not invent project commands.
4. Define evidence that proves the outcome: tests, build output, runtime walkthrough, screenshots, exported artifacts, API responses, diffs or logs.
5. Define allowed writes and protected paths explicitly.
6. Define an evidence-driven iteration policy and a finite retry/improvement budget.
7. Define completion and pause conditions as a matched pair.
8. Output the portable contract first. Add a Codex adapter when requested.
9. For a saved contract, run `python3 scripts/lint_task_contract.py <file>` from this skill directory.

## Default output

Use Chinese when the user writes Chinese. Do not leave placeholders in the final contract.

```text
任务契约
结果：交付一个可观察、可使用的具体结果。
验证：列出项目真实存在的检查命令，并至少完成一次核心流程；用命令输出、日志、截图、文件或链接证明结果。
约束：保持既有公共行为和无关模块不变；不引入未获授权的账号、付费服务、生产变更或敏感数据。
写入边界：只修改为该结果直接需要的目录和文件；明确列出禁止修改的路径。
迭代策略：先完成最小可验证版本；每次有意义的修改后重跑相关检查；同一问题连续失败两次后更换证据来源或缩小复现；最多进行三轮聚焦改进。
完成条件：核心结果有运行证据，相关检查通过；不能运行的检查及其原因已明确报告。
暂停条件：需要新的凭证、付费、生产权限、破坏性操作、外部账号操作、所有权判断，或关键产品方向不清时暂停并请求用户决定。
假设：列出为了继续而采用的低风险假设；没有则写“无”。
```

## Codex `/goal` adapter

When Codex goal syntax is useful, mirror the same contract without weakening it:

```text
/goal <concrete outcome>
Verification: <commands and observable evidence>
Constraints: <behavior and risk constraints>
Boundaries: <allowed writes and protected paths>
Iteration policy: <evidence-driven bounded retries>
Stop when: <completion proof>
Pause if: <human decision or external authority is required>
Assumptions: <low-risk assumptions or none>
```

Do not output `/目标`. Do not convert vague taste words such as“高级”or“专业”directly into acceptance criteria; translate them into reviewable screenshots, hierarchy, spacing, readability, consistency and bounded visual iterations.

## When the request is still materially ambiguous

Provide the safest recommended contract first, then at most three short choices:

```text
可选调整
1. 形态：A 本地最小版本（推荐） / B 修改现有项目 / C 先做原型
2. 范围：A 核心流程（推荐） / B 加常见增强 / C 完整产品
3. 验证：A 本地运行证据（推荐） / B 真机或集成环境 / C 发布前验证

你可以回复：按推荐，或 1B 2A 3C。
```

Ask an open question only if these choices would hide an important decision.

## Quality gate

Revise the contract when any of these are true:

- the result is merely“完成、优化、做得更好”;
- verification says only“确保可用”;
- the write boundary is the entire machine or repository without justification;
- retries are unlimited or do not require new evidence;
- high-risk actions lack explicit approval or pause conditions;
- the contract contains unresolved placeholders;
- completion depends only on the agent's confidence.

## Resources

- `scripts/lint_task_contract.py`: deterministic structure and placeholder check.
- `references/platform-adapters.md`: when to emit portable, Codex or compact forms.
- `evals/evals.json`: representative trigger and output tests.
