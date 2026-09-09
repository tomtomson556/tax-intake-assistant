from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from pydantic import BaseModel, model_validator

from tax_intake_assistant.models import MissingInformation, StructuredAssessment
from tax_intake_assistant.readiness import decide_readiness

CASES_DIR = Path(__file__).resolve().parent / "cases"
REQUIRED_IDS = [f"m2-{index:02d}" for index in range(1, 25)]
REQUIRED_TAGS = {
    "typos",
    "approximate",
    "contradiction",
    "multi_gap",
    "non_blocking_gap",
    "oos_plus_missing",
    "prompt_injection",
}
EXPECTED_READINESS_COUNTS = {
    "DRAFT_READY": 8,
    "CLARIFICATION_REQUIRED": 10,
    "ESCALATE": 6,
}


class GoldenMissing(BaseModel):
    concept: str
    blocking: bool
    follow_up_intent: str | None = None

    @model_validator(mode="after")
    def follow_up_when_blocking(self) -> GoldenMissing:
        if self.blocking and not (self.follow_up_intent or "").strip():
            raise ValueError("blocking missing_information requires follow_up_intent")
        return self


class Golden(BaseModel):
    must_contain_facts: list[str]
    must_not_invent: list[str]
    missing_information: list[GoldenMissing]
    review_point_concepts: list[str]
    uncertainty_concepts: list[str]
    out_of_scope: bool
    out_of_scope_reason_concept: str | None = None

    @model_validator(mode="after")
    def reason_when_out_of_scope(self) -> Golden:
        if self.out_of_scope and not (self.out_of_scope_reason_concept or "").strip():
            raise ValueError("out_of_scope requires out_of_scope_reason_concept")
        return self


class EvalCase(BaseModel):
    id: str
    title: str
    case_type: str
    tags: list[str]
    request_text: str
    golden: Golden


def load_cases(cases_dir: Path | None = None) -> list[EvalCase]:
    directory = cases_dir or CASES_DIR
    cases: list[EvalCase] = []
    for path in sorted(directory.glob("m2-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        case = EvalCase.model_validate(payload)
        if path.stem != case.id:
            raise ValueError(f"{path.name} does not match id {case.id!r}")
        cases.append(case)
    return cases


def expected_readiness(case: EvalCase):
    assessment = StructuredAssessment(
        case_summary=case.title,
        facts=list(case.golden.must_contain_facts) or [case.title],
        missing_information=[
            MissingInformation(
                description=item.concept,
                blocking=item.blocking,
                follow_up_question=item.follow_up_intent,
            )
            for item in case.golden.missing_information
        ],
        review_points=list(case.golden.review_point_concepts),
        uncertainties=list(case.golden.uncertainty_concepts),
        out_of_scope=case.golden.out_of_scope,
        out_of_scope_reason=case.golden.out_of_scope_reason_concept,
    )
    return decide_readiness(assessment)


def validate_dataset(cases: list[EvalCase] | None = None) -> list[EvalCase]:
    loaded = cases if cases is not None else load_cases()
    ids = [case.id for case in loaded]
    if ids != REQUIRED_IDS:
        raise ValueError(f"Expected ids {REQUIRED_IDS}, got {ids}")
    counts = Counter(expected_readiness(case).value for case in loaded)
    if dict(counts) != EXPECTED_READINESS_COUNTS:
        raise ValueError(
            "Expected readiness split "
            f"{EXPECTED_READINESS_COUNTS}, got {dict(counts)}"
        )
    present_tags = {tag for case in loaded for tag in case.tags}
    missing_tags = REQUIRED_TAGS - present_tags
    if missing_tags:
        raise ValueError(f"Dataset is missing required tags: {sorted(missing_tags)}")
    return loaded
