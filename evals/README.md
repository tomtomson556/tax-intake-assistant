# Eval set (M2)

Synthetic German intake cases for the real OpenAI provider. This is **not** product evaluation (M3): no LLM-judge, scoring framework, or product grade lives here.

## Privacy

Cases are synthetic. Names and firms are fictional. **M2 is not permission to send real client data to OpenAI.** Run demo and eval only with synthetic or demonstrably anonymized text.

## Layout

- `evals/cases/m2-01.json` … `m2-24.json`: one file per case, filename equals `id`
- `evals/dataset.py`: load and validate
- `evals/run.py`: optional live run against OpenAI
- `evals/results/`: local result JSON (gitignored)

## Golden conventions

Goldens describe concepts, not required model wording.

Readiness is **not** a second product rule in the JSON. It is derived by building a stub `StructuredAssessment` from the golden flags and calling the same `decide_readiness` gate as the application:

1. `out_of_scope` → `ESCALATE`
2. else any `blocking` missing-information item → `CLARIFICATION_REQUIRED`
3. else `DRAFT_READY`

Target split: 8 / 10 / 6.

`blocking` in a golden means: an internal draft is not reasonably possible without that information. That is eval authorship practice, not a `PRODUCT.md` catalogue and not a copy of `FakeProvider` amount/date regexes. Non-blocking gaps (for example a missing guest list when amount, date, and occasion are present) must not force `CLARIFICATION_REQUIRED`.

If `out_of_scope` is true, the gate escalates even when blocking gaps are also present (`m2-22`).

## Commands

Validate without a network call (also covered by pytest):

```bash
python -m evals.run --validate-only
```

Live run (requires `OPENAI_API_KEY`; always uses OpenAI, never FakeProvider):

```bash
export OPENAI_API_KEY=...
python -m evals.run
```

The runner calls `structure_case` and `decide_readiness` only. It does **not** generate drafts. It writes metadata (provider, model `gpt-5.6-sol`, reasoning effort `medium`, prompt version, git commit) plus per-case structured assessments to `evals/results/`. It does not print full request texts. A provider error is stored as `status=provider_error`, not as `ESCALATE`. If any case hits a provider error, the process exits with status 1. Readiness mismatches against the golden are reported, but they do not fail the process (that is M3).
