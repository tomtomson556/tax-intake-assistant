import os

from pydantic import ValidationError

from tax_intake_assistant.models import StructuredAssessment
from tax_intake_assistant.prompts import (
    ASSESSMENT_INSTRUCTIONS,
    DRAFT_INSTRUCTIONS,
    assessment_input,
    draft_input,
)
from tax_intake_assistant.provider import ProviderConfigError, ProviderError

OPENAI_MODEL = "gpt-5.6-sol"
REASONING_EFFORT = "medium"
_REASONING = {"effort": REASONING_EFFORT}


class OpenAIProvider:
    """OpenAI Responses API provider. Does not decide readiness."""

    def __init__(self, client: object | None = None) -> None:
        if client is not None:
            self._client = client
            return
        api_key = _require_api_key()
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)

    def structure_case(self, request_text: str) -> StructuredAssessment:
        try:
            response = self._client.responses.parse(
                model=OPENAI_MODEL,
                instructions=ASSESSMENT_INSTRUCTIONS,
                input=assessment_input(request_text),
                text_format=StructuredAssessment,
                reasoning=_REASONING,
                store=False,
            )
        except (ProviderError, ProviderConfigError):
            raise
        except Exception as exc:
            raise ProviderError(
                f"OpenAI request failed ({type(exc).__name__})."
            ) from exc
        _raise_if_unusable(response, expect_parsed=True)
        return _parsed_assessment(response)

    def compose_draft(
        self, request_text: str, assessment: StructuredAssessment
    ) -> str:
        try:
            response = self._client.responses.create(
                model=OPENAI_MODEL,
                instructions=DRAFT_INSTRUCTIONS,
                input=draft_input(request_text, assessment.model_dump_json()),
                reasoning=_REASONING,
                store=False,
            )
        except (ProviderError, ProviderConfigError):
            raise
        except Exception as exc:
            raise ProviderError(
                f"OpenAI request failed ({type(exc).__name__})."
            ) from exc
        _raise_if_unusable(response, expect_parsed=False)
        return _output_text(response)


def _require_api_key() -> str:
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise ProviderConfigError(
            "TAX_INTAKE_PROVIDER=openai requires OPENAI_API_KEY."
        )
    return api_key


def _raise_if_unusable(response: object, *, expect_parsed: bool) -> None:
    error = getattr(response, "error", None)
    if error:
        raise ProviderError("OpenAI request failed.")
    status = getattr(response, "status", None)
    if status is not None and status != "completed":
        raise ProviderError(f"OpenAI response was {status}.")
    refusal = _refusal_message(response)
    if refusal:
        raise ProviderError("OpenAI refused to process this request.")
    if expect_parsed and getattr(response, "output_parsed", None) is None:
        raise ProviderError("OpenAI did not return a parsed StructuredAssessment.")


def _parsed_assessment(response: object) -> StructuredAssessment:
    parsed = response.output_parsed
    if isinstance(parsed, StructuredAssessment):
        return parsed
    try:
        return StructuredAssessment.model_validate(parsed)
    except ValidationError as exc:
        raise ProviderError(
            "OpenAI returned an invalid structured assessment."
        ) from exc


def _refusal_message(response: object) -> str | None:
    for item in getattr(response, "output", None) or []:
        for part in getattr(item, "content", None) or []:
            if getattr(part, "type", None) == "refusal":
                return getattr(part, "refusal", None) or "refused"
            refusal = getattr(part, "refusal", None)
            if refusal:
                return str(refusal)
    return None


def _output_text(response: object) -> str:
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()
    chunks: list[str] = []
    for item in getattr(response, "output", None) or []:
        for part in getattr(item, "content", None) or []:
            if getattr(part, "type", None) == "output_text":
                chunks.append(getattr(part, "text", "") or "")
    joined = "".join(chunks).strip()
    if not joined:
        raise ProviderError("OpenAI did not return draft text.")
    return joined
