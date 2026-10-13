import pytest
from pydantic import ValidationError

from app.schemas import ParticipantCreate


def has_available_capacity(current_count: int, max_capacity: int) -> bool:
    """Return True if the event has at least one available place."""
    return current_count < max_capacity


def check_duplicate_registration(registered_ids: list[int], new_id: int) -> None:
    """Raise ValueError when the participant is already registered."""
    if new_id in registered_ids:
        raise ValueError("Participant is already registered")


# 1. Happy-path tests

def test_valid_participant(sample_participant_dict):
    participant = ParticipantCreate(**sample_participant_dict)

    assert participant.name == "Jane Doe"
    assert participant.email == "jane.doe@example.com"


def test_capacity_available():
    assert has_available_capacity(5, 10) is True


def test_new_registration_is_not_duplicate():
    check_duplicate_registration([1, 2, 3], 4)


# 2. Boundary tests for capacity

def test_capacity_one_place_remaining():
    assert has_available_capacity(9, 10) is True


def test_capacity_exactly_full():
    assert has_available_capacity(10, 10) is False


def test_capacity_exceeded():
    assert has_available_capacity(11, 10) is False


# 3. Negative tests

def test_invalid_email(sample_participant_dict):
    participant_data = sample_participant_dict.copy()
    participant_data["email"] = "not-an-email"

    with pytest.raises(ValidationError):
        ParticipantCreate(**participant_data)


def test_participant_name_too_short(sample_participant_dict):
    participant_data = sample_participant_dict.copy()
    participant_data["name"] = "A"

    with pytest.raises(ValidationError):
        ParticipantCreate(**participant_data)


def test_duplicate_registration_raises_error():
    with pytest.raises(ValueError, match="already registered"):
        check_duplicate_registration([1, 2, 3], 2)
