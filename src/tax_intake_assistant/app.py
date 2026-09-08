from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tax_intake_assistant.provider import FakeProvider, Provider
from tax_intake_assistant.workflow import InvalidRequestError, process_intake

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


def create_app(provider: Provider | None = None) -> FastAPI:
    provider = provider or FakeProvider()
    app = FastAPI(title="Tax Intake Assistant")

    @app.get("/", response_class=HTMLResponse)
    def intake_form(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "intake.html",
            {"error": None, "request_text": ""},
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
                {"error": str(exc), "request_text": request_text},
                status_code=400,
            )
        return templates.TemplateResponse(request, "result.html", {"case": processed})

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("tax_intake_assistant.app:app", host="127.0.0.1", port=8000)
