
"""Student B - Participant and registration unit tests."""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models import Event, Participant, Registration
from app.schemas import ParticipantCreate
from app.routers.participants import (
    create_participant,
    list_participants,
    get_participant,
    delete_participant,
)
from app.routers.registrations import (
    has_available_capacity,
    check_duplicate_registration,
    register_participant,
    list_event_participants,
)


# ======================= DATABASE MOCKS =======================

def mock_db(first_result=None, all_result=None):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = first_result
    db.query.return_value.order_by.return_value.all.return_value = (
        all_result if all_result is not None else []
    )
    return db


def mock_registration_db(*results):
    """Return successive results for registration queries."""
    db = MagicMock()
    db.query.return_value.filter.return_value.first.side_effect = list(results)
    return db


def make_event(capacity=10, registrations=None):
    event = MagicMock(spec=Event)
    event.id = 1
    event.capacity = capacity
    event.registrations = registrations if registrations is not None else []
    return event


def make_participant():
    participant = MagicMock(spec=Participant)
    participant.id = 2
    participant.name = "Amine Benali"
    participant.email = "amine@example.com"
    return participant


# ======================= PARTICIPANT VALIDATION =======================

def test_valid_participant_creation(sample_participant_dict):
    participant = ParticipantCreate.model_validate(sample_participant_dict)

    assert participant.name == "Amine Benali"
    assert participant.email == "amine@example.com"


def test_name_minimum_length_boundary(sample_participant_dict):
    data = dict(sample_participant_dict, name="Al")

    assert ParticipantCreate.model_validate(data).name == "Al"


@pytest.mark.parametrize(
    "bad_email",
    ["not-an-email", "missing-at.com", "@no-user.com", "user@", ""],
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


# ======================= PARTICIPANT API =======================

def test_create_participant_success(sample_participant_dict):
    db = mock_db()
    payload = ParticipantCreate.model_validate(sample_participant_dict)

    result = create_participant(payload, db)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)
    assert result.name == "Amine Benali"
    assert result.email == "amine@example.com"


def test_create_participant_duplicate_email(sample_participant_dict):
    existing = Participant(
        name="Amine Benali",
        email="amine@example.com",
    )
    db = mock_db(first_result=existing)
    payload = ParticipantCreate.model_validate(sample_participant_dict)

    with pytest.raises(HTTPException) as exc:
        create_participant(payload, db)

    assert exc.value.status_code == 409
    db.add.assert_not_called()


def test_list_participants_returns_list():
    people = [
        Participant(name="Amine Benali", email="amine@example.com"),
        Participant(name="Sara Ali", email="sara@example.com"),
    ]
    db = mock_db(all_result=people)

    assert list_participants(db) == people


def test_get_participant_success():
    person = Participant(name="Amine Benali", email="amine@example.com")
    db = mock_db(first_result=person)

    assert get_participant(1, db) == person


def test_get_participant_not_found():
    db = mock_db()

    with pytest.raises(HTTPException) as exc:
        get_participant(999, db)

    assert exc.value.status_code == 404


def test_delete_participant_success():
    person = Participant(name="Amine Benali", email="amine@example.com")
    db = mock_db(first_result=person)

    delete_participant(1, db)

    db.delete.assert_called_once_with(person)
    db.commit.assert_called_once()


def test_delete_participant_not_found():
    db = mock_db()

    with pytest.raises(HTTPException) as exc:
        delete_participant(999, db)

    assert exc.value.status_code == 404
    db.delete.assert_not_called()


# ======================= REGISTRATION API =======================

def test_register_participant_success():
    event = make_event()
    person = make_participant()
    db = mock_registration_db(event, person, None)

    result = register_participant(1, 2, db)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)
    assert result.event_id == 1
    assert result.participant_id == 2


def test_register_event_not_found():
    db = mock_registration_db(None)

    with pytest.raises(HTTPException) as exc:
        register_participant(999, 2, db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Event not found."
    db.add.assert_not_called()


def test_register_participant_not_found():
    event = make_event()
    db = mock_registration_db(event, None)

    with pytest.raises(HTTPException) as exc:
        register_participant(1, 999, db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Participant not found."


def test_register_duplicate_participant():
    event = make_event()
    person = make_participant()
    existing = MagicMock(spec=Registration)
    db = mock_registration_db(event, person, existing)

    with pytest.raises(HTTPException) as exc:
        register_participant(1, 2, db)

    assert exc.value.status_code == 409
    assert exc.value.detail == "Participant is already registered."
    db.add.assert_not_called()


def test_register_when_event_is_full():
    event = make_event(capacity=1, registrations=[MagicMock()])
    person = make_participant()
    db = mock_registration_db(event, person, None)

    with pytest.raises(HTTPException) as exc:
        register_participant(1, 2, db)

    assert exc.value.status_code == 409
    assert exc.value.detail == "Event capacity has been reached."
    db.add.assert_not_called()


def test_list_event_participants_success():
    event = make_event()
    person = make_participant()

    registration = MagicMock()
    registration.participant = person
    event.registrations = [registration]

    db = mock_db(first_result=event)

    result = list_event_participants(1, db)

    assert result == [
        {
            "id": 2,
            "name": "Amine Benali",
            "email": "amine@example.com",
        }
    ]


def test_list_event_participants_event_not_found():
    db = mock_db()

    with pytest.raises(HTTPException) as exc:
        list_event_participants(999, db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Event not found."

# ===== Lab 2: Student B required helper tests =====

def test_has_available_capacity_when_space_left():
    assert has_available_capacity(5, 10) is True


def test_capacity_current_one_below_max():
    assert has_available_capacity(9, 10) is True


def test_capacity_current_equals_max():
    assert has_available_capacity(10, 10) is False


def test_capacity_current_above_max():
    assert has_available_capacity(11, 10) is False


def test_no_duplicate_registration_passes():
    check_duplicate_registration([1, 2, 3], 4)


def test_duplicate_registration_raises_value_error():
    with pytest.raises(
        ValueError,
        match="^Participant is already registered\\.$"
    ):
        check_duplicate_registration([1, 2, 3], 2)

