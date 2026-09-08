from fastapi.testclient import TestClient

from tax_intake_assistant.app import create_app

DRAFT_READY_REQUEST = (
    "Our client purchased a used delivery van on 12.03.2024 for EUR 28.500. "
    "Business use is about 80 percent. Please assess deductibility and input tax."
)
CLARIFICATION_REQUEST = "Client wants to know if a new laptop is deductible."
ESCALATE_REQUEST = (
    "The client received a criminal investigation letter for suspected tax evasion."
)


def test_intake_form_is_served() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "Unstructured client request" in response.text
    assert 'name="request_text"' in response.text
    assert "deterministic FakeProvider" in response.text
    assert "not a real AI model" in response.text


def test_empty_submit_returns_form_error() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/", data={"request_text": "  "})
    assert response.status_code == 400
    assert "A client request is required." in response.text
    assert 'name="request_text"' in response.text


def test_draft_ready_case_shows_unreviewed_internal_draft() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/", data={"request_text": DRAFT_READY_REQUEST})
    assert response.status_code == 200
    assert "Readiness: DRAFT_READY" in response.text
    assert "deterministic FakeProvider" in response.text
    assert "Follow-up questions" not in response.text
    assert "Status: UNREVIEWED" in response.text
    assert 'id="internal-draft"' in response.text
    assert "INTERNAL FILE NOTE" in response.text
    assert "not client communication" in response.text.lower()


def test_clarification_case_does_not_include_a_draft() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/", data={"request_text": CLARIFICATION_REQUEST})
    assert response.status_code == 200
    assert "Readiness: CLARIFICATION_REQUIRED" in response.text
    assert "(blocking)" in response.text
    assert "Amount of the expense is missing." in response.text
    assert "What is the amount of the expense?" in response.text
    assert "What is the date of the transaction?" in response.text
    assert "Follow-up questions" in response.text
    assert 'id="internal-draft"' not in response.text
    assert "UNREVIEWED" not in response.text


def test_out_of_scope_case_escalates_without_a_draft() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/", data={"request_text": ESCALATE_REQUEST})
    assert response.status_code == 200
    assert "Readiness: ESCALATE" in response.text
    assert "outside ordinary operational tax work" in response.text
    assert 'id="internal-draft"' not in response.text
    assert "UNREVIEWED" not in response.text


def test_result_page_escapes_request_html() -> None:
    payload = (
        "<script>alert(1)</script> bought a delivery van on 2024-03-12 for EUR 1000."
    )
    with TestClient(create_app()) as client:
        response = client.post("/", data={"request_text": payload})
    assert response.status_code == 200
    assert "<script>alert(1)</script>" not in response.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text
