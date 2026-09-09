import os
from collections.abc import Mapping

from tax_intake_assistant.provider import FakeProvider, Provider, ProviderConfigError

PROVIDER_ENV = "TAX_INTAKE_PROVIDER"
API_KEY_ENV = "OPENAI_API_KEY"


def build_provider(environ: Mapping[str, str] | None = None) -> Provider:
    env = os.environ if environ is None else environ
    name = (env.get(PROVIDER_ENV) or "fake").strip().lower()
    if name in {"", "fake"}:
        return FakeProvider()
    if name == "openai":
        if not (env.get(API_KEY_ENV) or "").strip():
            raise ProviderConfigError(
                "TAX_INTAKE_PROVIDER=openai requires OPENAI_API_KEY."
            )
        from tax_intake_assistant.openai_provider import OpenAIProvider

        return OpenAIProvider()
    raise ProviderConfigError(
        f"Unknown provider {name!r}. Use 'fake' or 'openai'."
    )
