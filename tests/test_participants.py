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

def test_capacity_empty_event():
    assert has_available_capacity(0, 10) is True


def test_capacity_zero_limit():
    assert has_available_capacity(0, 0) is False


def test_duplicate_registration_in_empty_list():
    check_duplicate_registration([], 1)


def test_duplicate_registration_with_repeated_ids():
    with pytest.raises(ValueError, match="already registered"):
        check_duplicate_registration([1, 1, 2], 1)


def test_participant_name_at_minimum_length(sample_participant_dict):
    participant_data = sample_participant_dict.copy()
    participant_data["name"] = "Jo"

    participant = ParticipantCreate(**participant_data)

    assert participant.name == "Jo"

def test_create_participant_api(client, sample_participant_dict):
    response = client.post(
        "/participants/",
        json=sample_participant_dict,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane.doe@example.com"
    assert "id" in data


def test_create_participant_with_invalid_email_api(client, sample_participant_dict):
    participant_data = sample_participant_dict.copy()
    participant_data["email"] = "not-an-email"

    response = client.post("/participants/", json=participant_data)

    assert response.status_code == 422


def test_create_participant_with_short_name_api(client, sample_participant_dict):
    participant_data = sample_participant_dict.copy()
    participant_data["name"] = "A"

    response = client.post("/participants/", json=participant_data)

    assert response.status_code == 422


def test_duplicate_participant_email_api(client, sample_participant_dict):
    first = client.post("/participants/", json=sample_participant_dict)
    second = client.post("/participants/", json=sample_participant_dict)

    assert first.status_code == 201
    assert second.status_code == 409


def test_list_participants_api(client, sample_participant_dict):
    client.post("/participants/", json=sample_participant_dict)

    response = client.get("/participants/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_participant_api(client, sample_participant_dict):
    create_response = client.post(
        "/participants/",
        json=sample_participant_dict,
    )
    participant_id = create_response.json()["id"]

    response = client.get(f"/participants/{participant_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"


def test_get_missing_participant_api(client):
    response = client.get("/participants/99999")

    assert response.status_code == 404


def test_delete_participant_api(client, sample_participant_dict):
    create_response = client.post(
        "/participants/",
        json=sample_participant_dict,
    )
    participant_id = create_response.json()["id"]

    response = client.delete(f"/participants/{participant_id}")

    assert response.status_code == 204
    assert client.get(f"/participants/{participant_id}").status_code == 404

def test_register_participant_success_api(client, sample_event_dict, sample_participant_dict):
    event_response = client.post("/events/", json=sample_event_dict)
    participant_response = client.post("/participants/", json=sample_participant_dict)

    assert event_response.status_code == 201
    assert participant_response.status_code == 201

    event_id = event_response.json()["id"]
    participant_id = participant_response.json()["id"]

    response = client.post(
        f"/events/{event_id}/register/{participant_id}"
    )

    assert response.status_code == 201
    assert response.json()["event_id"] == event_id
    assert response.json()["participant_id"] == participant_id


def test_duplicate_registration_rejected_api(client, sample_event_dict, sample_participant_dict):
    event_response = client.post("/events/", json=sample_event_dict)
    participant_response = client.post("/participants/", json=sample_participant_dict)

    event_id = event_response.json()["id"]
    participant_id = participant_response.json()["id"]

    first = client.post(f"/events/{event_id}/register/{participant_id}")
    second = client.post(f"/events/{event_id}/register/{participant_id}")

    assert first.status_code == 201
    assert second.status_code == 409


def test_event_capacity_reached_api(client, sample_event_dict, sample_participant_dict):
    event_data = sample_event_dict.copy()
    event_data["capacity"] = 1

    event_response = client.post("/events/", json=event_data)
    assert event_response.status_code == 201
    event_id = event_response.json()["id"]

    first_participant = client.post(
        "/participants/",
        json=sample_participant_dict,
    )

    second_participant_data = {
        "name": "John Smith",
        "email": "john.smith@example.com",
    }
    second_participant = client.post(
        "/participants/",
        json=second_participant_data,
    )

    assert first_participant.status_code == 201
    assert second_participant.status_code == 201

    first_registration = client.post(
        f"/events/{event_id}/register/{first_participant.json()['id']}"
    )
    second_registration = client.post(
        f"/events/{event_id}/register/{second_participant.json()['id']}"
    )

    assert first_registration.status_code == 201
    assert second_registration.status_code == 409
