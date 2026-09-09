from collections import Counter

from evals.dataset import (
    EXPECTED_READINESS_COUNTS,
    REQUIRED_IDS,
    REQUIRED_TAGS,
    expected_readiness,
    load_cases,
    validate_dataset,
)


def test_eval_dataset_structure_and_gate_split() -> None:
    cases = validate_dataset()
    assert [case.id for case in cases] == REQUIRED_IDS
    assert [case.id for case in load_cases()] == REQUIRED_IDS
    present_tags = {tag for case in cases for tag in case.tags}
    assert REQUIRED_TAGS <= present_tags
    counts = Counter(expected_readiness(case).value for case in cases)
    assert dict(counts) == EXPECTED_READINESS_COUNTS
    for case in cases:
        assert case.request_text.strip()
        for item in case.golden.missing_information:
            if item.blocking:
                assert (item.follow_up_intent or "").strip()
        if case.golden.out_of_scope:
            assert (case.golden.out_of_scope_reason_concept or "").strip()
