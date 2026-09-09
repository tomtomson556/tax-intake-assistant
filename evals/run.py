from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from evals.dataset import EvalCase, expected_readiness, load_cases, validate_dataset
from tax_intake_assistant import __version__
from tax_intake_assistant.openai_provider import (
    OPENAI_MODEL,
    REASONING_EFFORT,
    OpenAIProvider,
)
from tax_intake_assistant.prompts import PROMPT_VERSION
from tax_intake_assistant.provider import ProviderConfigError, ProviderError
from tax_intake_assistant.readiness import decide_readiness

RESULTS_DIR = Path(__file__).resolve().parent / "results"
REPO_ROOT = Path(__file__).resolve().parent.parent


def evaluate_case(case: EvalCase, provider) -> dict[str, object]:
    expected = expected_readiness(case).value
    record: dict[str, object] = {
        "id": case.id,
        "status": "ok",
        "error_type": None,
        "expected_readiness": expected,
        "actual_readiness": None,
        "assessment": None,
    }
    try:
        assessment = provider.structure_case(case.request_text)
        actual = decide_readiness(assessment).value
    except ProviderError as exc:
        record["status"] = "provider_error"
        record["error_type"] = type(exc).__name__
        return record
    record["actual_readiness"] = actual
    record["assessment"] = assessment.model_dump()
    return record


def run_eval(cases: list[EvalCase], provider, output_dir: Path) -> int:
    records: list[dict[str, object]] = []
    matches = 0
    provider_errors = 0
    for case in cases:
        record = evaluate_case(case, provider)
        records.append(record)
        if record["status"] == "provider_error":
            provider_errors += 1
            print(f"{case.id} provider_error {record['error_type']}")
            continue
        actual = record["actual_readiness"]
        if actual == record["expected_readiness"]:
            matches += 1
        print(f"{case.id} ok {actual}")

    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{PROMPT_VERSION}-{_git_commit()[:12]}-{stamp}.json"
    output_path = output_dir / filename
    payload = {
        "meta": {
            "provider": "openai",
            "model": OPENAI_MODEL,
            "reasoning_effort": REASONING_EFFORT,
            "prompt_version": PROMPT_VERSION,
            "git_commit": _git_commit(),
            "package_version": __version__,
        },
        "cases": records,
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {_display_path(output_path)}")
    print(f"Readiness matches golden: {matches}/{len(cases)}")
    return 1 if provider_errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the M2 eval set against OpenAI.")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the dataset without calling a provider.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=RESULTS_DIR,
        help="Directory for result JSON files (gitignored).",
    )
    args = parser.parse_args(argv)

    cases = validate_dataset(load_cases())
    print(f"Validated {len(cases)} eval cases.")
    if args.validate_only:
        return 0

    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        print("OPENAI_API_KEY is required for the eval run.")
        return 2
    try:
        provider = OpenAIProvider(api_key=api_key)
    except ProviderConfigError as exc:
        print(str(exc))
        return 2
    return run_eval(cases, provider, args.output_dir)


def _display_path(path: Path) -> Path:
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
