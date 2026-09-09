from tax_intake_assistant.models import MissingInformation, ReadinessState
from tax_intake_assistant.readiness import decide_readiness


def test_out_of_scope_escalates(make_assessment) -> None:
    assessment = make_assessment(
        out_of_scope=True,
        out_of_scope_reason="Criminal tax matter.",
        missing_information=[
            MissingInformation(
                description="Amount missing",
                blocking=True,
                follow_up_question="What is the amount?",
            ),
        ],
    )
    assert decide_readiness(assessment) == ReadinessState.ESCALATE


def test_blocking_gap_requires_clarification(make_assessment) -> None:
    assessment = make_assessment(
        missing_information=[
            MissingInformation(
                description="Date missing",
                blocking=True,
                follow_up_question="What is the date of the transaction?",
            ),
        ]
    )
    assert decide_readiness(assessment) == ReadinessState.CLARIFICATION_REQUIRED


def test_non_blocking_gap_is_draft_ready(make_assessment) -> None:
    assessment = make_assessment(
        missing_information=[
            MissingInformation(
                description="Written confirmation not on file",
                blocking=False,
            ),
        ],
        uncertainties=["Business-use share is approximate."],
    )
    assert decide_readiness(assessment) == ReadinessState.DRAFT_READY


def test_complete_in_scope_case_is_draft_ready(make_assessment) -> None:
    assert decide_readiness(make_assessment()) == ReadinessState.DRAFT_READY
