from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from evals.dataset import expected_readiness, load_cases, validate_dataset
from tax_intake_assistant import __version__
from tax_intake_assistant.openai_provider import (
    OPENAI_MODEL,
    REASONING_EFFORT,
    OpenAIProvider,
)
from tax_intake_assistant.prompts import PROMPT_VERSION
from tax_intake_assistant.provider import ProviderConfigError, ProviderError
from tax_intake_assistant.workflow import process_intake

RESULTS_DIR = Path(__file__).resolve().parent / "results"
REPO_ROOT = Path(__file__).resolve().parent.parent


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

    try:
        provider = OpenAIProvider()
    except ProviderConfigError as exc:
        print(str(exc))
        return 2

    records: list[dict[str, object]] = []
    matches = 0
    for case in cases:
        expected = expected_readiness(case).value
        record: dict[str, object] = {
            "id": case.id,
            "status": "ok",
            "error_type": None,
            "expected_readiness": expected,
            "actual_readiness": None,
            "assessment": None,
            "draft_produced": False,
        }
        try:
            processed = process_intake(case.request_text, provider)
        except ProviderError as exc:
            record["status"] = "provider_error"
            record["error_type"] = type(exc).__name__
            print(f"{case.id} provider_error {type(exc).__name__}")
        else:
            actual = processed.readiness.value
            record["actual_readiness"] = actual
            record["assessment"] = processed.assessment.model_dump()
            record["draft_produced"] = processed.draft is not None
            if actual == expected:
                matches += 1
            print(f"{case.id} ok {actual}")
        records.append(record)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{PROMPT_VERSION}-{_git_commit()[:12]}-{stamp}.json"
    output_path = args.output_dir / filename
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
    print(f"Wrote {output_path.relative_to(REPO_ROOT)}")
    print(f"Readiness matches golden: {matches}/{len(cases)}")
    return 0


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
