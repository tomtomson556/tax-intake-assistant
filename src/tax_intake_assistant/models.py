from enum import StrEnum

from pydantic import BaseModel, model_validator


class ReadinessState(StrEnum):
    ESCALATE = "ESCALATE"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    DRAFT_READY = "DRAFT_READY"


class DraftStatus(StrEnum):
    UNREVIEWED = "UNREVIEWED"


class MissingInformation(BaseModel):
    description: str
    blocking: bool
    follow_up_question: str | None = None


class StructuredAssessment(BaseModel):
    case_summary: str
    facts: list[str]
    missing_information: list[MissingInformation]
    review_points: list[str]
    uncertainties: list[str]
    out_of_scope: bool
    out_of_scope_reason: str | None = None

    @model_validator(mode="after")
    def require_reason_when_out_of_scope(self) -> "StructuredAssessment":
        if self.out_of_scope and not (self.out_of_scope_reason or "").strip():
            raise ValueError(
                "out_of_scope_reason is required when out_of_scope is true"
            )
        return self


class Draft(BaseModel):
    body: str
    status: DraftStatus = DraftStatus.UNREVIEWED


class ProcessedCase(BaseModel):
    request_text: str
    assessment: StructuredAssessment
    readiness: ReadinessState
    draft: Draft | None = None
    follow_up_questions: list[str] = []

    @model_validator(mode="after")
    def draft_only_when_ready_and_unreviewed(self) -> "ProcessedCase":
        if self.readiness == ReadinessState.DRAFT_READY:
            if self.draft is None:
                raise ValueError("DRAFT_READY cases must include a draft")
            if self.draft.status != DraftStatus.UNREVIEWED:
                raise ValueError("Every draft must start as UNREVIEWED")
        elif self.draft is not None:
            raise ValueError("Drafts are produced only for DRAFT_READY")
        return self
