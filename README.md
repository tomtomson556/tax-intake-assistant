# Tax Intake Assistant

AI-assisted intake and drafting for German tax advisory teams.

**Status:** M2 one real provider and eval set. OpenAI (`gpt-5.6-sol`) plus FakeProvider, exact readiness gate, and a small server-rendered UI. Drafts are produced only for `DRAFT_READY` and start as `UNREVIEWED`.

- Product (V1): [`PRODUCT.md`](PRODUCT.md)
- Sequencing: [`ROADMAP.md`](ROADMAP.md)
- Agent instructions: [`AGENTS.md`](AGENTS.md)
- Eval set: [`evals/README.md`](evals/README.md)

## Privacy boundary

M2 is **not** a release for sending real client data to a model provider. Use the UI and eval runner only with synthetic or demonstrably anonymized text. API keys stay in the environment; `.env` is gitignored and not auto-loaded.

## Setup

Python 3.12+:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Copy [`.env.example`](.env.example) only as documentation. Export variables in the shell; do not commit secrets.

## Provider choice

`TAX_INTAKE_PROVIDER` is `fake` (default) or `openai`. There is no silent fallback from OpenAI to FakeProvider.

| Value | Behavior |
| --- | --- |
| unset / `fake` | Deterministic `FakeProvider`. Safe for tests and offline demo. |
| `openai` | `OpenAIProvider` with hardcoded model `gpt-5.6-sol` and `reasoning.effort=medium`. Requires `OPENAI_API_KEY`. Missing key fails at process start. |

Tests always inject `FakeProvider` and do not make live API calls.

## Run

FakeProvider (default):

```bash
python -m tax_intake_assistant
```

or:

```bash
uvicorn tax_intake_assistant.app:create_runtime_app --factory --reload
```

OpenAI demo (synthetic text only):

```bash
export TAX_INTAKE_PROVIDER=openai
export OPENAI_API_KEY=...
python -m tax_intake_assistant
```

Open http://127.0.0.1:8000

A technical provider failure is returned as HTTP 502 with no assessment and no draft. It is not an `ESCALATE` outcome.

## Eval run

```bash
python -m evals.run --validate-only
export OPENAI_API_KEY=...
python -m evals.run
```

See [`evals/README.md`](evals/README.md). Live eval is not part of CI.

## Checks

```bash
ruff check .
pytest
```
