# Tax Intake Assistant

AI-assisted intake and drafting for German tax advisory teams.

**Status:** M1 deterministic vertical slice. FakeProvider, exact readiness gate, and a small server-rendered UI. Drafts are produced only for `DRAFT_READY` and start as `UNREVIEWED`.

- Product (V1): [`PRODUCT.md`](PRODUCT.md)
- Sequencing: [`ROADMAP.md`](ROADMAP.md)
- Agent instructions: [`AGENTS.md`](AGENTS.md)

## Setup

Python 3.12+:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Run

```bash
uvicorn tax_intake_assistant.app:app --reload
```

Open http://127.0.0.1:8000

## Checks

```bash
ruff check .
pytest
```
