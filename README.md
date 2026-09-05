# Tax Intake Assistant

AI-assisted intake and drafting for German tax advisory teams.

**Status:** M0 repository foundation. **M1 is not implemented yet.** There is no intake workflow, readiness engine, or draft generation.

- Product (V1): [`PRODUCT.md`](PRODUCT.md)
- Sequencing: [`ROADMAP.md`](ROADMAP.md)
- Agent instructions: [`AGENTS.md`](AGENTS.md)

## Setup

Python 3.12+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks

```bash
ruff check .
pytest
```
