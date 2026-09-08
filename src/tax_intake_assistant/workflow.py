from tax_intake_assistant.models import (
    Draft,
    DraftStatus,
    ProcessedCase,
    ReadinessState,
)
from tax_intake_assistant.provider import Provider
from tax_intake_assistant.readiness import decide_readiness


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
    )
