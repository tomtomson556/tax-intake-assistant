import pytest
from fastapi.testclient import TestClient

from tax_intake_assistant.app import create_app, create_runtime_app
from tax_intake_assistant.config import build_provider
from tax_intake_assistant.openai_provider import OpenAIProvider
from tax_intake_assistant.provider import FakeProvider, ProviderConfigError


def test_default_provider_is_fake(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAX_INTAKE_PROVIDER", raising=False)
    assert isinstance(build_provider(), FakeProvider)


def test_explicit_fake_ignores_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAX_INTAKE_PROVIDER", "fake")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert isinstance(build_provider(), FakeProvider)


def test_openai_without_key_fails_at_build(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAX_INTAKE_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ProviderConfigError, match="OPENAI_API_KEY"):
        build_provider()


def test_openai_blank_key_does_not_fall_back_to_fake(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TAX_INTAKE_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "  ")
    with pytest.raises(ProviderConfigError, match="OPENAI_API_KEY"):
        build_provider()


def test_unknown_provider_fails_at_build(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAX_INTAKE_PROVIDER", "anthropic")
    with pytest.raises(ProviderConfigError, match="Unknown provider"):
        build_provider()


def test_openai_with_key_builds_openai_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TAX_INTAKE_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-build")
    provider = build_provider()
    assert isinstance(provider, OpenAIProvider)
    assert provider._client.api_key == "sk-from-build"


def test_runtime_app_fails_before_serving_when_openai_key_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TAX_INTAKE_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ProviderConfigError, match="OPENAI_API_KEY"):
        create_runtime_app()


def test_create_app_stays_fake_even_if_env_selects_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TAX_INTAKE_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with TestClient(create_app()) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "deterministic FakeProvider" in response.text
