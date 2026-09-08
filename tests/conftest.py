import pytest

from tax_intake_assistant.models import StructuredAssessment


@pytest.fixture
def make_assessment():
    def _make(**overrides: object) -> StructuredAssessment:
        payload: dict[str, object] = {
            "case_summary": "Company van purchase",
            "facts": ["Client bought a delivery van."],
            "missing_information": [],
            "review_points": ["Confirm business versus private use."],
            "uncertainties": [],
            "out_of_scope": False,
            "out_of_scope_reason": None,
        }
        payload.update(overrides)
        return StructuredAssessment.model_validate(payload)

    return _make
