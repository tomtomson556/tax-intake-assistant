import os

from tax_intake_assistant.openai_provider import OpenAIProvider
from tax_intake_assistant.provider import FakeProvider, Provider, ProviderConfigError

PROVIDER_ENV = "TAX_INTAKE_PROVIDER"
API_KEY_ENV = "OPENAI_API_KEY"


def build_provider() -> Provider:
    name = (os.environ.get(PROVIDER_ENV) or "fake").strip().lower()
    if name in {"", "fake"}:
        return FakeProvider()
    if name == "openai":
        api_key = (os.environ.get(API_KEY_ENV) or "").strip()
        if not api_key:
            raise ProviderConfigError(
                "TAX_INTAKE_PROVIDER=openai requires OPENAI_API_KEY."
            )
        return OpenAIProvider(api_key=api_key)
    raise ProviderConfigError(
        f"Unknown provider {name!r}. Use 'fake' or 'openai'."
    )
