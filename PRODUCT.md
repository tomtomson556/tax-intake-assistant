# Product (V1)

Canonical V1 definition for Tax Intake Assistant. Other files should link here instead of restating this.

## What this is

An **AI-assisted intake and drafting** tool for **German tax advisory teams** (Steuerberatungskanzleien).

It helps a firm assemble a matter, decide whether work can proceed, and prepare an internal draft for a human advisor. It is **not** a robot tax advisor and **not** a client-facing filing product.

## Users

- **Primary:** tax advisors and Kanzlei staff preparing intake and first drafts.
- **Not a delivery channel:** clients do not receive advice or documents from the system automatically.

## V1 outcome

Given an intake (facts, questions, and any attached material), the product must:

1. Decide exactly one **readiness** state.
2. Either escalate, request clarification, or prepare a draft.
3. Leave every draft **unreviewed** until a human reviews it.
4. Never give autonomous tax advice and never deliver to the client on its own.

## Readiness

Readiness is decided by **deterministic application code**, not by a model judging the case.

Exactly one of:

| State | Meaning |
| --- | --- |
| `ESCALATE` | A human must take over. Do not draft. |
| `CLARIFICATION_REQUIRED` | Missing or ambiguous information blocks a responsible draft. Do not draft. |
| `DRAFT_READY` | The intake is sufficient to produce an internal draft. |

A **draft may be produced only for `DRAFT_READY`**.

Escalate when the matter is out of scope, high-risk, legally sensitive, or otherwise unfit for an unattended draft. Ask for clarification when the gap is concrete and answerable. Draft only when neither applies.

## Drafts and review

- A draft is an **internal** artifact for the advisor (for example a letter or file note), not client-ready output.
- Every produced draft is `UNREVIEWED` until human review.
- Human review is required before any use as client communication.
- The system must not send, file, or otherwise deliver a draft to a client.

## Hard invariants

These are non-negotiable for V1:

- Readiness states are only `ESCALATE`, `CLARIFICATION_REQUIRED`, and `DRAFT_READY`.
- The readiness decision is deterministic application code.
- Drafts are produced only for `DRAFT_READY`.
- Every draft remains `UNREVIEWED` until human review.
- No autonomous tax advice.
- No automatic client delivery.

## In scope for V1

- Structured intake for German tax advisory work.
- Deterministic readiness gating.
- Draft generation **gated** by `DRAFT_READY`.
- Human review before anything leaves the firm.

## Out of scope for V1

- Autonomous or unsupervised tax advice.
- Automatic sending to clients.
- ELSTER / official filing.
- Replacing the licensed Steuerberater.
- A general-purpose legal chatbot.

Engineering sequencing (what exists now vs later) lives in [`ROADMAP.md`](ROADMAP.md), not here.
