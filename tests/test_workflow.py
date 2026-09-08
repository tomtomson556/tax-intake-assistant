import pytest

from tax_intake_assistant.models import DraftStatus, MissingInformation, ReadinessState
from tax_intake_assistant.workflow import InvalidRequestError, process_intake


class RecordingProvider:
    def __init__(self, assessment, draft_body: str = "SHOULD NOT APPEAR") -> None:
        self.assessment = assessment
        self.draft_body = draft_body
        self.draft_calls = 0

    def structure_case(self, request_text: str):
        return self.assessment

    def compose_draft(self, request_text: str, assessment) -> str:
        self.draft_calls += 1
        return self.draft_body


@pytest.mark.parametrize("request_text", ["", "   ", "\n\t"])
def test_empty_request_is_rejected(request_text: str, make_assessment) -> None:
    provider = RecordingProvider(make_assessment())
    with pytest.raises(InvalidRequestError, match="required"):
        process_intake(request_text, provider)
    assert provider.draft_calls == 0


def test_escalate_does_not_compose_a_draft(make_assessment) -> None:
    provider = RecordingProvider(
        make_assessment(
            out_of_scope=True,
            out_of_scope_reason="Matter is outside ordinary operational tax work.",
            missing_information=[
                MissingInformation(
                    description="Amount of the expense is missing.",
                    blocking=True,
                    follow_up_question="What is the amount of the expense?",
                ),
            ],
        )
    )
    processed = process_intake("Client faces a criminal investigation.", provider)
    assert processed.readiness == ReadinessState.ESCALATE
    assert processed.draft is None
    assert processed.follow_up_questions == []
    assert provider.draft_calls == 0


def test_clarification_does_not_compose_a_draft(make_assessment) -> None:
    provider = RecordingProvider(
        make_assessment(
            missing_information=[
                MissingInformation(
                    description="Amount of the expense is missing.",
                    blocking=True,
                    follow_up_question="What is the amount of the expense?",
                ),
                MissingInformation(
                    description="Written confirmation not on file",
                    blocking=False,
                    follow_up_question="Can you provide written confirmation?",
                ),
            ]
        )
    )
    processed = process_intake("Client bought a laptop.", provider)
    assert processed.readiness == ReadinessState.CLARIFICATION_REQUIRED
    assert processed.draft is None
    assert processed.follow_up_questions == ["What is the amount of the expense?"]
    assert provider.draft_calls == 0


def test_draft_ready_produces_unreviewed_internal_draft(make_assessment) -> None:
    provider = RecordingProvider(
        make_assessment(),
        draft_body="INTERNAL FILE NOTE — not client communication",
    )
    processed = process_intake(
        "  Client bought a van on 2024-03-12 for EUR 28500.  ",
        provider,
    )
    assert processed.request_text == (
        "Client bought a van on 2024-03-12 for EUR 28500."
    )
    assert processed.readiness == ReadinessState.DRAFT_READY
    assert processed.follow_up_questions == []
    assert processed.draft is not None
    assert processed.draft.status == DraftStatus.UNREVIEWED
    assert processed.draft.body == "INTERNAL FILE NOTE — not client communication"
    assert provider.draft_calls == 1
