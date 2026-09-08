from tax_intake_assistant.models import ReadinessState, StructuredAssessment


def decide_readiness(assessment: StructuredAssessment) -> ReadinessState:
    """Apply the deterministic V1 readiness gate. Not a model judgment."""
    if assessment.out_of_scope:
        return ReadinessState.ESCALATE
    if any(item.blocking for item in assessment.missing_information):
        return ReadinessState.CLARIFICATION_REQUIRED
    return ReadinessState.DRAFT_READY
