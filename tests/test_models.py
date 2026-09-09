import pytest
from pydantic import ValidationError

from tax_intake_assistant.models import MissingInformation


def test_blocking_item_requires_follow_up_question() -> None:
    with pytest.raises(ValidationError, match="follow_up_question"):
        MissingInformation(description="Amount missing", blocking=True)


def test_blocking_item_rejects_blank_follow_up_question() -> None:
    with pytest.raises(ValidationError, match="follow_up_question"):
        MissingInformation(
            description="Amount missing",
            blocking=True,
            follow_up_question="   ",
        )


def test_blocking_item_accepts_concrete_follow_up() -> None:
    item = MissingInformation(
        description="Amount missing",
        blocking=True,
        follow_up_question="What is the amount of the expense?",
    )
    assert item.follow_up_question == "What is the amount of the expense?"


def test_non_blocking_item_does_not_require_follow_up() -> None:
    item = MissingInformation(
        description="Guest list not on file",
        blocking=False,
    )
    assert item.follow_up_question is None
