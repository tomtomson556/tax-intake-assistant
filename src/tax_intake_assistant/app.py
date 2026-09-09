from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tax_intake_assistant.config import build_provider
from tax_intake_assistant.openai_provider import OpenAIProvider
from tax_intake_assistant.provider import FakeProvider, Provider, ProviderError
from tax_intake_assistant.workflow import InvalidRequestError, process_intake

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

_FAKE_BANNER = (
    "M2 demo: this uses a deterministic FakeProvider, not a real AI model. "
    "Do not send real client data."
)
_OPENAI_BANNER = (
    "M2 demo: this uses OpenAI (gpt-5.6-sol) for demo and eval only. "
    "Do not send real client data to the provider. "
    "This is not a release for productive use of real client data."
)


def create_app(provider: Provider | None = None) -> FastAPI:
    provider = provider or FakeProvider()
    banner = _banner_for(provider)
    app = FastAPI(title="Tax Intake Assistant")

    @app.get("/", response_class=HTMLResponse)
    def intake_form(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "intake.html",
            {"error": None, "request_text": "", "provider_banner": banner},
        )

    @app.post("/", response_class=HTMLResponse)
    def submit_request(
        request: Request,
        request_text: str = Form(default=""),
    ) -> HTMLResponse:
        try:
            processed = process_intake(request_text, provider)
        except InvalidRequestError as exc:
            return templates.TemplateResponse(
                request,
                "intake.html",
                {
                    "error": str(exc),
                    "request_text": request_text,
                    "provider_banner": banner,
                },
                status_code=400,
            )
        except ProviderError as exc:
            return templates.TemplateResponse(
                request,
                "intake.html",
                {
                    "error": str(exc),
                    "request_text": request_text,
                    "provider_banner": banner,
                },
                status_code=502,
            )
        return templates.TemplateResponse(
            request,
            "result.html",
            {"case": processed, "provider_banner": banner},
        )

    return app


def create_runtime_app() -> FastAPI:
    """ASGI factory: select the provider from the environment at process start."""
    return create_app(build_provider())


def _banner_for(provider: Provider) -> str:
    if isinstance(provider, OpenAIProvider):
        return _OPENAI_BANNER
    return _FAKE_BANNER


def main() -> None:
    import uvicorn

    uvicorn.run(create_runtime_app(), host="127.0.0.1", port=8000)
