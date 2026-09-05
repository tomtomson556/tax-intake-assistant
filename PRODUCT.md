# Product (V1)

Canonical V1 definition for Tax Intake Assistant. Other files should link here instead of restating this.

## What this is

An **AI-assisted intake and drafting** tool for small and medium-sized **German tax advisory firms** (Steuerberatungskanzleien).

Input is an **unstructured client request**. The product structures the case, applies a deterministic readiness gate, and may prepare an **internal draft** for a human reviewer. It is **not** a robot tax advisor and **not** a client-facing delivery or filing product.

## Users

- **Primary:** Steuerfachangestellte in small and medium-sized German tax advisory firms who regularly handle client requests from sole proprietors and small businesses.
- **Not a delivery channel:** clients do not receive advice or documents from the system automatically.

## Workflow

1. Validate input.
2. Structure the case.
3. Identify relevant facts.
4. Detect missing or unclear information.
5. Determine review points.
6. Mark uncertainties.
7. Apply the deterministic readiness gate.
8. Produce clarification, escalation, or an internal draft.
9. Human review.

## Structured assessment

Every processed case includes:

- `case_summary`
- `facts`
- `missing_information` (each item has a `blocking` indicator)
- `review_points`
- `uncertainties`
- `out_of_scope`
- `out_of_scope_reason`

## Readiness gate

Readiness is decided by **deterministic application code**, not by a model judging the case.

Exactly one of:

| State | Meaning |
| --- | --- |
| `ESCALATE` | A human must take over. Do not draft. |
| `CLARIFICATION_REQUIRED` | At least one blocking information gap. Do not draft. |
| `DRAFT_READY` | The case is sufficient to produce an internal draft. |

Exact rule, in this order:

1. If `out_of_scope = true` → `ESCALATE`
2. Else if at least one blocking information gap → `CLARIFICATION_REQUIRED`
3. Else → `DRAFT_READY`

A **draft is produced only for `DRAFT_READY`**.

## Drafts and review

- A draft is an **internal** artifact (for example a letter or file note), not client-ready output.
- Every produced draft starts as `UNREVIEWED`.
- Human review is required before any use as client communication.
- Human-review grades are `A`, `B`, `C`, and `D`.
- The system must not send, file, or otherwise deliver a draft to a client.

## Hard invariants

These are non-negotiable for V1:

- Readiness states are only `ESCALATE`, `CLARIFICATION_REQUIRED`, and `DRAFT_READY`.
- The readiness decision is deterministic application code and follows the exact gate above.
- Drafts are produced only for `DRAFT_READY`.
- Every draft starts as `UNREVIEWED`.
- No autonomous tax advice.
- No automatic client delivery.

## In scope for V1

Ordinary operational tax cases, such as:

- vehicle purchase / leasing
- business / private use
- equipment
- travel
- entertainment
- training
- home office
- missing invoices
- depreciation
- simple input-tax questions

Also in scope: unstructured request in, structured assessment, deterministic readiness gating, draft generation gated by `DRAFT_READY`, and human review before anything leaves the firm.

## Out of scope for V1

- Autonomous or unsupervised tax advice.
- Automatic sending to clients.
- ELSTER / official filing.
- Replacing the licensed Steuerberater.
- A general-purpose legal chatbot.

Matters outside ordinary operational tax work are `out_of_scope` and therefore `ESCALATE`.

## Success metrics

- **Primary:** time to a professionally acceptable draft.
- **Initial hypothesis:** at least 30% processing-time reduction.

Additional metrics: readiness accuracy, false readiness rate, missing-information recall, correctness, hallucination rate, and draft acceptance.

Engineering sequencing (what exists now vs later) lives in [`ROADMAP.md`](ROADMAP.md), not here.
