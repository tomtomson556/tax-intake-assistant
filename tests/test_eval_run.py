from pathlib import Path

from evals.dataset import load_cases
from evals.run import evaluate_case, run_eval

from tax_intake_assistant.models import StructuredAssessment
from tax_intake_assistant.provider import ProviderError
from tax_intake_assistant.readiness import decide_readiness


class _StructureOnlyProvider:
    def __init__(self, assessment: StructuredAssessment) -> None:
        self.assessment = assessment
        self.structure_calls = 0
        self.draft_calls = 0

    def structure_case(self, request_text: str) -> StructuredAssessment:
        self.structure_calls += 1
        return self.assessment

    def compose_draft(self, request_text: str, assessment: StructuredAssessment) -> str:
        self.draft_calls += 1
        raise AssertionError("eval must not compose a draft")


class _FailingProvider:
    def structure_case(self, request_text: str) -> StructuredAssessment:
        raise ProviderError("OpenAI request failed (RuntimeError).")

    def compose_draft(self, request_text: str, assessment: StructuredAssessment) -> str:
        raise AssertionError("eval must not compose a draft")


def test_evaluate_case_uses_gate_without_composing_a_draft() -> None:
    case = load_cases()[0]
    assessment = StructuredAssessment(
        case_summary=case.title,
        facts=["Laptopkauf der Demo-Mandantin."],
        missing_information=[],
        review_points=[],
        uncertainties=[],
        out_of_scope=False,
        out_of_scope_reason=None,
    )
    provider = _StructureOnlyProvider(assessment)
    record = evaluate_case(case, provider)
    assert record["status"] == "ok"
    assert record["actual_readiness"] == decide_readiness(assessment).value
    assert provider.structure_calls == 1
    assert provider.draft_calls == 0


def test_run_eval_exits_nonzero_only_for_provider_errors(tmp_path: Path) -> None:
    cases = load_cases()[:2]
    failing = _FailingProvider()
    assert run_eval(cases, failing, tmp_path) == 1

    ready = StructuredAssessment(
        case_summary="ok",
        facts=["Laptopkauf."],
        missing_information=[],
        review_points=[],
        uncertainties=[],
        out_of_scope=False,
        out_of_scope_reason=None,
    )
    mixed_cases = load_cases()[7:9]
    provider = _StructureOnlyProvider(ready)
    assert run_eval(mixed_cases, provider, tmp_path) == 0
    assert provider.draft_calls == 0
