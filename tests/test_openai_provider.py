from types import SimpleNamespace

import pytest

from tax_intake_assistant.models import (
    MissingInformation,
    ReadinessState,
    StructuredAssessment,
)
from tax_intake_assistant.openai_provider import (
    ASSESSMENT_MAX_OUTPUT_TOKENS,
    DRAFT_MAX_OUTPUT_TOKENS,
    OPENAI_MAX_RETRIES,
    OPENAI_MODEL,
    OPENAI_TIMEOUT_SECONDS,
    REASONING_EFFORT,
    OpenAIProvider,
)
from tax_intake_assistant.prompts import PROMPT_VERSION
from tax_intake_assistant.provider import ProviderConfigError, ProviderError
from tax_intake_assistant.workflow import process_intake

VALID_ASSESSMENT = StructuredAssessment(
    case_summary="Laptopkauf der Demo-Mandantin Hanna Frost",
    facts=["Kauf eines Laptops am 02.02.2024 für 890 EUR."],
    missing_information=[],
    review_points=["Rechnung prüfen."],
    uncertainties=[],
    out_of_scope=False,
    out_of_scope_reason=None,
)


class FakeResponses:
    def __init__(
        self,
        *,
        parse_response: object | None = None,
        parse_error: Exception | None = None,
        create_response: object | None = None,
        create_error: Exception | None = None,
    ) -> None:
        self.parse_response = parse_response
        self.parse_error = parse_error
        self.create_response = create_response
        self.create_error = create_error
        self.parse_calls: list[dict[str, object]] = []
        self.create_calls: list[dict[str, object]] = []

    def parse(self, **kwargs: object) -> object:
        self.parse_calls.append(kwargs)
        if self.parse_error is not None:
            raise self.parse_error
        assert self.parse_response is not None
        return self.parse_response

    def create(self, **kwargs: object) -> object:
        self.create_calls.append(kwargs)
        if self.create_error is not None:
            raise self.create_error
        assert self.create_response is not None
        return self.create_response


class FakeClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


def _provider(responses: FakeResponses) -> OpenAIProvider:
    return OpenAIProvider(client=FakeClient(responses))


def test_structure_case_uses_structured_output_and_fixed_model() -> None:
    responses = FakeResponses(
        parse_response=SimpleNamespace(
            output_parsed=VALID_ASSESSMENT,
            status="completed",
            error=None,
            output=[],
        )
    )
    assessment = _provider(responses).structure_case("Laptop der Demo-Mandantin.")
    assert assessment == VALID_ASSESSMENT
    kwargs = responses.parse_calls[0]
    assert kwargs["model"] == OPENAI_MODEL
    assert kwargs["text_format"] is StructuredAssessment
    assert kwargs["reasoning"] == {"effort": REASONING_EFFORT}
    assert kwargs["store"] is False
    assert kwargs["max_output_tokens"] == ASSESSMENT_MAX_OUTPUT_TOKENS
    assert PROMPT_VERSION == "m2-v1"


def test_refusal_is_a_provider_error_not_readiness() -> None:
    refusal_part = SimpleNamespace(type="refusal", refusal="refused")
    message = SimpleNamespace(content=[refusal_part])
    responses = FakeResponses(
        parse_response=SimpleNamespace(
            output_parsed=None,
            status="completed",
            error=None,
            output=[message],
        )
    )
    with pytest.raises(ProviderError, match="refused"):
        _provider(responses).structure_case("Laptop der Demo-Mandantin.")


def test_invalid_parsed_payload_is_a_provider_error() -> None:
    responses = FakeResponses(
        parse_response=SimpleNamespace(
            output_parsed={
                "case_summary": "Out of scope without reason",
                "facts": [],
                "missing_information": [],
                "review_points": [],
                "uncertainties": [],
                "out_of_scope": True,
                "out_of_scope_reason": None,
            },
            status="completed",
            error=None,
            output=[],
        )
    )
    with pytest.raises(ProviderError, match="invalid structured assessment"):
        _provider(responses).structure_case("Laptop der Demo-Mandantin.")


def test_incomplete_response_is_a_provider_error() -> None:
    responses = FakeResponses(
        parse_response=SimpleNamespace(
            output_parsed=None,
            status="incomplete",
            error=None,
            output=[],
        )
    )
    with pytest.raises(ProviderError, match="incomplete"):
        _provider(responses).structure_case("Laptop der Demo-Mandantin.")


def test_api_exception_is_a_provider_error() -> None:
    responses = FakeResponses(parse_error=RuntimeError("network down"))
    with pytest.raises(ProviderError, match="OpenAI request failed"):
        _provider(responses).structure_case("Laptop der Demo-Mandantin.")
    assert responses.create_calls == []


def test_structure_error_does_not_compose_a_draft() -> None:
    responses = FakeResponses(parse_error=RuntimeError("network down"))
    provider = _provider(responses)
    with pytest.raises(ProviderError):
        process_intake("Laptop der Demo-Mandantin.", provider)
    assert responses.create_calls == []


def test_draft_call_error_does_not_yield_a_processed_case() -> None:
    responses = FakeResponses(
        parse_response=SimpleNamespace(
            output_parsed=VALID_ASSESSMENT,
            status="completed",
            error=None,
            output=[],
        ),
        create_error=RuntimeError("draft failed"),
    )
    with pytest.raises(ProviderError, match="OpenAI request failed"):
        process_intake(
            "Demo-Mandantin Hanna Frost kaufte am 02.02.2024 einen Laptop für 890 EUR.",
            _provider(responses),
        )


def test_compose_draft_uses_same_model_and_does_not_store() -> None:
    responses = FakeResponses(
        create_response=SimpleNamespace(
            output_text="INTERNAL FILE NOTE — not client communication",
            status="completed",
            error=None,
            output=[],
        )
    )
    body = _provider(responses).compose_draft("request", VALID_ASSESSMENT)
    assert "INTERNAL FILE NOTE" in body
    kwargs = responses.create_calls[0]
    assert kwargs["model"] == OPENAI_MODEL
    assert kwargs["reasoning"] == {"effort": REASONING_EFFORT}
    assert kwargs["store"] is False
    assert kwargs["max_output_tokens"] == DRAFT_MAX_OUTPUT_TOKENS


def test_openai_provider_requires_api_key_without_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ProviderConfigError, match="OPENAI_API_KEY"):
        OpenAIProvider()


def test_openai_client_uses_passed_key_timeout_and_no_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env")
    provider = OpenAIProvider(api_key="sk-test")
    assert provider._client.api_key == "sk-test"
    assert provider._client.max_retries == OPENAI_MAX_RETRIES
    timeout = provider._client.timeout
    timeout_seconds = getattr(timeout, "timeout", timeout)
    assert timeout_seconds == OPENAI_TIMEOUT_SECONDS


def test_blocking_assessment_from_openai_still_uses_application_gate() -> None:
    assessment = StructuredAssessment(
        case_summary="Laptop ohne Betrag",
        facts=["Mandantin fragt nach einem Laptop."],
        missing_information=[
            MissingInformation(
                description="Betrag fehlt.",
                blocking=True,
                follow_up_question="Wie hoch war der Kaufpreis?",
            )
        ],
        review_points=[],
        uncertainties=[],
        out_of_scope=False,
        out_of_scope_reason=None,
    )
    responses = FakeResponses(
        parse_response=SimpleNamespace(
            output_parsed=assessment,
            status="completed",
            error=None,
            output=[],
        )
    )
    processed = process_intake("Laptop der Demo-Mandantin.", _provider(responses))
    assert processed.readiness == ReadinessState.CLARIFICATION_REQUIRED
    assert processed.draft is None
    assert responses.create_calls == []
