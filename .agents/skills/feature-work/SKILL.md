---
name: feature-work
description: Implement repository features from product context through focused verification and a Draft PR. Use for user-visible changes that must preserve hard product invariants.
---

# Feature work

## Establish context

Follow the source-of-truth order in the root `AGENTS.md`. Inspect current `main`, open pull requests, and local Git state, then read only the relevant product, roadmap, code, and test context.

Define the requested user behavior and affected hard invariants before editing. Prefer the smallest end-to-end change that satisfies them. Do not introduce architecture, dependencies, providers, persistence, or infrastructure unless the task and canonical documents require them.

## Implement and verify

1. Implement the narrowest coherent change.
2. Add the smallest high-signal test set that proves user behavior, hard invariants, and meaningful failure paths. Do not optimize for test volume or mirror implementation details.
3. Run focused checks while iterating, then all checks required by the repository.
4. Critically review the final diff for correctness, scope drift, invariant regressions, needless complexity, and tests that could pass despite broken behavior. Fix findings and rerun affected checks.

## Deliver

Inspect the final diff and worktree before staging only task-related changes. After successful checks, follow the root `AGENTS.md` Git and pull-request rules: commit conventionally, push with upstream tracking, and create or update a Draft PR with goal, scope, non-goals, and verification results.

Do not report completion if checks fail or required delivery steps are blocked. Never merge or mark the PR ready unless explicitly requested.
