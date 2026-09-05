# Roadmap

Sequencing only. Product rules live in [`PRODUCT.md`](PRODUCT.md).

## M0 — Product definition and repository foundation (completed)

Canonical V1 product definition, shared docs, Python package skeleton, bootstrap test, and CI.

This milestone does **not** include the business workflow.

## M1 — Deterministic vertical slice (next)

First application path with a **FakeProvider** and a small **server-rendered UI**: unstructured request in, structured assessment, exact readiness gate, draft only when `DRAFT_READY`, every draft `UNREVIEWED`.

**Not implemented yet.**

## M2 — One real provider and eval set

Exactly **one** real provider, structured output, prompt version, and 20–30 eval cases.

## M3 — Product evaluation

Product evaluation and error analysis against the metrics in [`PRODUCT.md`](PRODUCT.md).

## M4 — Packaging and deployment decision

Packaging, Docker, reproducible start, and a deployment decision.

Cloud remains **optional and deferred**. Do not add cloud infrastructure unless a later milestone explicitly requires it.

Do not implement a later milestone until the current one is the work in progress.
