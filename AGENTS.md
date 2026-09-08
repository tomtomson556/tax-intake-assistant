# Agent instructions

Shared task and context router for Cursor and Codex. Keep repository-wide direction here and reusable workflows in project skills.

## Source of truth

Inspect live state first, then apply sources in this order:

1. Current `main`
2. [`PRODUCT.md`](PRODUCT.md)
3. [`ROADMAP.md`](ROADMAP.md)
4. Accepted ADRs
5. Code and tests

Do not weaken the invariants in `PRODUCT.md`. Do not restate product rules or milestone status here.

Before recommending a branch, architecture, provider, security, persistence, deployment, cloud, or system-wide dependency change, inspect current `main`, open pull requests, local git state, the canonical files above, and the affected code and tests.

## Task routing

- Feature or behavior work: follow [`.agents/skills/feature-work/SKILL.md`](.agents/skills/feature-work/SKILL.md).
- Product scope and hard invariants: read [`PRODUCT.md`](PRODUCT.md).
- Milestone scope and sequencing: read [`ROADMAP.md`](ROADMAP.md).
- Setup and required checks: read [`README.md`](README.md).
- Otherwise, load only the affected code, tests, and accepted ADRs needed for the task.

## Project map

- Package: `src/tax_intake_assistant/`
- Tests: `tests/`
- Eval cases: `evals/cases/`

## Git and pull requests

- Never commit directly to `main`.
- Work on a small, focused branch.
- After successful checks, commit all task-related changes with a clear conventional commit message.
- Push the branch with upstream tracking.
- Create or update a Draft Pull Request containing goal, scope, non-goals, and verification results.
- Never merge the PR or mark it ready for review unless explicitly requested.
- Never hide failing checks or claim success when blocked.
