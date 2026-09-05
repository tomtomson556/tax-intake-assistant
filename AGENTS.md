# Agent instructions

Shared by Cursor and Codex. This file is an index, not a handbook. Do not copy it into `.cursor/rules` or a large `.codex/config.toml`.

## Source of truth

Inspect live state first, then apply sources in this order:

1. Current `main`
2. [`PRODUCT.md`](PRODUCT.md)
3. [`ROADMAP.md`](ROADMAP.md)
4. Accepted ADRs
5. Code and tests

Do not weaken the invariants in `PRODUCT.md`. Do not restate product rules or milestone status here.

Before recommending a branch, architecture, provider, security, persistence, deployment, cloud, or system-wide dependency change, inspect current `main`, open pull requests, local git state, the canonical files above, and the affected code and tests.

## Current work

Follow [`ROADMAP.md`](ROADMAP.md) for what is done, next, and later. Do not add a real AI provider, database, RAG, Docker, cloud, MCP server, or custom skills unless the current milestone requires it.

## Layout

- Package: `src/tax_intake_assistant/`
- Tests: `tests/`
- Eval cases: `evals/cases/`

## Checks

`ruff check .` and `pytest`. See [`README.md`](README.md).

## Git and pull requests

- Never commit directly to `main`.
- Work on a small, focused branch.
- After successful checks, commit all task-related changes with a clear conventional commit message.
- Push the branch with upstream tracking.
- Create or update a Draft Pull Request containing goal, scope, non-goals, and verification results.
- Never merge the PR or mark it ready for review unless explicitly requested.
- Never hide failing checks or claim success when blocked.
