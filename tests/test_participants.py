"""Student B - Participant and registration logic unit tests."""
import pytest
from pydantic import ValidationError

from app.schemas import ParticipantCreate
from app.routers.registrations import (
    has_available_capacity,
    check_duplicate_registration,
)


# ======================= HAPPY PATH (2+) =======================
def test_valid_participant_creation(sample_participant_dict):
    participant = ParticipantCreate.model_validate(sample_participant_dict)
    assert participant.name == "Amine Benali"
    assert participant.email == "amine@example.com"


def test_has_available_capacity_when_space_left():
    assert has_available_capacity(5, 10) is True


def test_no_duplicate_registration_passes():
    # Should not raise
    assert check_duplicate_registration([1, 2, 3], 4) is None


# ======================= BOUNDARY VALUES (3+) =======================
def test_capacity_current_one_below_max():
    assert has_available_capacity(9, 10) is True


def test_capacity_current_equals_max():
    assert has_available_capacity(10, 10) is False


def test_capacity_current_above_max():
    assert has_available_capacity(11, 10) is False


def test_name_minimum_length_boundary(sample_participant_dict):
    data = dict(sample_participant_dict, name="Al")
    assert ParticipantCreate.model_validate(data).name == "Al"


# ======================= NEGATIVE TESTS (2+) =======================
@pytest.mark.parametrize(
    "bad_email", ["not-an-email", "missing-at.com", "@no-user.com", "user@", ""]
)
def test_invalid_email_raises(sample_participant_dict, bad_email):
    data = dict(sample_participant_dict, email=bad_email)
    with pytest.raises(ValidationError):
        ParticipantCreate.model_validate(data)


@pytest.mark.parametrize("short_name", ["", "A"])
def test_short_name_raises(sample_participant_dict, short_name):
    data = dict(sample_participant_dict, name=short_name)
    with pytest.raises(ValidationError):
        ParticipantCreate.model_validate(data)


def test_duplicate_registration_raises_value_error():
    with pytest.raises(ValueError):
        check_duplicate_registration([1, 2, 3], 2)