import re
from typing import Protocol

from tax_intake_assistant.models import MissingInformation, StructuredAssessment

_OUT_OF_SCOPE_RE = re.compile(
    r"(?i)("
    r"\belster\b|official filing|tax evasion|steuerhinterziehung|"
    r"criminal investigation|strafverfahren|\bdivorce\b|\bscheidung\b|"
    r"\binsolvency\b|\binsolvenz\b|\berbrecht\b|inheritance tax"
    r")"
)
_AMOUNT_RE = re.compile(
    r"(?i)(?:€|eur(?:o)?s?)\s*[\d.,]+|[\d.,]+\s*(?:€|eur(?:o)?s?)"
)
_DATE_RE = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[./]\d{1,2}[./]\d{2,4})\b")
_APPROXIMATE_RE = re.compile(
    r"(?i)\b(?:about|approximately|circa|unsure|unclear|ca\.)\b"
)
_USE_SPLIT_RE = re.compile(
    r"(?i)\b(?:car|van|vehicle|pkw|leasing|home office|home-office|dienstwagen)\b"
)


class Provider(Protocol):
    def structure_case(self, request_text: str) -> StructuredAssessment: ...

    def compose_draft(
        self, request_text: str, assessment: StructuredAssessment
    ) -> str: ...


class FakeProvider:
    """Deterministic stand-in for a model. Does not decide readiness."""

    def structure_case(self, request_text: str) -> StructuredAssessment:
        if _OUT_OF_SCOPE_RE.search(request_text):
            return StructuredAssessment(
                case_summary=_summary(request_text),
                facts=_facts(request_text),
                missing_information=[],
                review_points=[],
                uncertainties=[],
                out_of_scope=True,
                out_of_scope_reason="Matter is outside ordinary operational tax work.",
            )

        missing: list[MissingInformation] = []
        if _AMOUNT_RE.search(request_text) is None:
            missing.append(
                MissingInformation(
                    description="Amount of the expense is missing.",
                    blocking=True,
                    follow_up_question="What is the amount of the expense?",
                )
            )
        if _DATE_RE.search(request_text) is None:
            missing.append(
                MissingInformation(
                    description="Date of the transaction is missing.",
                    blocking=True,
                    follow_up_question="What is the date of the transaction?",
                )
            )

        review_points = ["Verify supporting invoices before any client communication."]
        if _USE_SPLIT_RE.search(request_text):
            review_points.append("Confirm business versus private use.")

        uncertainties: list[str] = []
        if _APPROXIMATE_RE.search(request_text):
            uncertainties.append("At least one stated fact is approximate or unclear.")

        return StructuredAssessment(
            case_summary=_summary(request_text),
            facts=_facts(request_text),
            missing_information=missing,
            review_points=review_points,
            uncertainties=uncertainties,
            out_of_scope=False,
            out_of_scope_reason=None,
        )

    def compose_draft(self, request_text: str, assessment: StructuredAssessment) -> str:
        facts = "\n".join(f"- {fact}" for fact in assessment.facts) or "- None recorded"
        review = (
            "\n".join(f"- {point}" for point in assessment.review_points)
            or "- None recorded"
        )
        return (
            "INTERNAL FILE NOTE — not client communication\n"
            "Human review is required before any use as client communication.\n\n"
            f"Summary\n{assessment.case_summary}\n\n"
            f"Facts\n{facts}\n\n"
            f"Review points\n{review}\n\n"
            "Do not send, file, or otherwise deliver this note to the client."
        )


def _summary(request_text: str) -> str:
    first_line = request_text.strip().splitlines()[0]
    if len(first_line) <= 200:
        return first_line
    return first_line[:197] + "..."


def _facts(request_text: str) -> list[str]:
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", request_text.strip())]
    return [part for part in parts if part]
