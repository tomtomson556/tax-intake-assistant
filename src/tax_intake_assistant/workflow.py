from tax_intake_assistant.models import (
    Draft,
    DraftStatus,
    ProcessedCase,
    ReadinessState,
    StructuredAssessment,
)
from tax_intake_assistant.provider import Provider
from tax_intake_assistant.readiness import decide_readiness

_MISSING_SUFFIX = " is missing"


class InvalidRequestError(ValueError):
    """Raised when the unstructured request cannot be processed."""


def validate_request(request_text: str) -> str:
    cleaned = request_text.strip()
    if not cleaned:
        raise InvalidRequestError("A client request is required.")
    return cleaned


def process_intake(request_text: str, provider: Provider) -> ProcessedCase:
    cleaned = validate_request(request_text)
    assessment = provider.structure_case(cleaned)
    readiness = decide_readiness(assessment)
    draft = None
    if readiness == ReadinessState.DRAFT_READY:
        draft = Draft(
            body=provider.compose_draft(cleaned, assessment),
            status=DraftStatus.UNREVIEWED,
        )
    return ProcessedCase(
        request_text=cleaned,
        assessment=assessment,
        readiness=readiness,
        draft=draft,
        follow_up_questions=_follow_up_questions(assessment, readiness),
    )


def _follow_up_questions(
    assessment: StructuredAssessment, readiness: ReadinessState
) -> list[str]:
    if readiness != ReadinessState.CLARIFICATION_REQUIRED:
        return []
    return [
        _follow_up_question(item.description)
        for item in assessment.missing_information
        if item.blocking
    ]


def _follow_up_question(description: str) -> str:
    text = description.strip().rstrip(".")
    if text.endswith("?"):
        return text
    if text.lower().endswith(_MISSING_SUFFIX):
        subject = text[: -len(_MISSING_SUFFIX)].strip()
        if subject:
            return f"What is the {subject[0].lower() + subject[1:]}?"
    return f"Can you provide this missing information: {text}?"
