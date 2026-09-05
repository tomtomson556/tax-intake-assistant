# Agent instructions

Shared by Cursor and Codex. This file is an index, not a handbook. Do not copy it into `.cursor/rules` or a large `.codex/config.toml`.

## Canonical sources

| File | Read for |
| --- | --- |
| [`PRODUCT.md`](PRODUCT.md) | V1 product, readiness, drafts, review, hard invariants |
| [`ROADMAP.md`](ROADMAP.md) | What is done, what is next, what is later |
| [`README.md`](README.md) | Setup and current status |

Do not weaken the invariants in `PRODUCT.md`. Do not duplicate them here.

## Current work

Follow [`ROADMAP.md`](ROADMAP.md). M1 is not implemented. Do not add a real AI provider, database, RAG, Docker, cloud, MCP server, or custom skills unless the current milestone requires it.

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
