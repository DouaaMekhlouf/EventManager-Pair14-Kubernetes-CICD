"""Student A - Event schema, search and endpoint-logic unit tests (no DB, no HTTP)."""
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas import EventCreate, EventUpdate
from app.routers.events import (
    create_event,
    delete_event,
    filter_events_by_location,
    filter_events_by_title,
    get_event,
    list_events,
    update_event,
)


# ---------------------------- helpers ----------------------------
def event_payload(base: dict, overrides: dict = None) -> dict:
    data = dict(base)
    data.update(overrides or {})
    return data


def make_event(base: dict, overrides: dict = None) -> EventCreate:
    return EventCreate.model_validate(event_payload(base, overrides))


def future_date():
    return date.today() + timedelta(days=30)


def past_date():
    return date.today() - timedelta(days=1)


def fake_db(first=None, rows=None):
    """A fake SQLAlchemy session: every query step returns the same fake query."""
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value = query
    query.order_by.return_value = query
    query.first.return_value = first
    query.all.return_value = rows if rows is not None else []
    return db


# ======================= HAPPY PATH (2+) =======================
def test_valid_event_creation(sample_event_dict):
    event = EventCreate.model_validate(sample_event_dict)
    assert event.title == "Python Meetup"
    assert event.capacity == 50


def test_filter_events_by_location_case_insensitive(prepopulated_event_store):
    result = filter_events_by_location(prepopulated_event_store, "ALGIERS")
    assert len(result) == 2  # "Algiers" and "algiers"


def test_filter_events_by_title_case_insensitive(prepopulated_event_store):
    result = filter_events_by_title(prepopulated_event_store, "python")
    assert len(result) == 1
    assert result[0].title == "Python Meetup"


def test_filter_events_by_title_mixed_case(prepopulated_event_store):
    """Kills string lowercasing mutants in event title filters."""
    result = filter_events_by_title(prepopulated_event_store, "PyThOn mEeTuP")
    assert len(result) == 1
    assert result[0].title == "Python Meetup"


def test_filter_events_no_match_returns_empty(prepopulated_event_store):
    assert filter_events_by_location(prepopulated_event_store, "Paris") == []


# ======================= BOUNDARY VALUES (3+) =======================
def test_capacity_minimum_boundary(sample_event_dict):
    assert make_event(sample_event_dict, {"capacity": 1}).capacity == 1


def test_capacity_maximum_boundary(sample_event_dict):
    """Kills relational operator mutants changing capacity > 10000 or <= 10000."""
    assert make_event(sample_event_dict, {"capacity": 10_000}).capacity == 10_000


def test_title_length_minimum_boundary(sample_event_dict):
    """Checks the minimum valid title length boundary (len > 2)."""
    assert make_event(sample_event_dict, {"title": "abc"}).title == "abc"


# ======================= NEGATIVE TESTS (2+) =======================
@pytest.mark.parametrize("short_title", ["", "a", "ab"])
def test_title_too_short_raises(sample_event_dict, short_title):
    """Kills mutants modifying title length logic (e.g., len > 2 to >= 2)."""
    with pytest.raises(ValidationError):
        make_event(sample_event_dict, {"title": short_title})


@pytest.mark.parametrize("bad_capacity", [0, -1, -100, 10_001])
def test_capacity_out_of_bounds_raises(sample_event_dict, bad_capacity):
    """Kills mutants bypassing upper and lower capacity boundaries."""
    with pytest.raises(ValidationError):
        make_event(sample_event_dict, {"capacity": bad_capacity})


# ======================= ENDPOINT LOGIC (fake db, called directly) =======================
def test_create_event_saves_and_returns_event(sample_event_dict):
    db = fake_db()
    event = make_event(sample_event_dict, {"date": future_date()})
    result = create_event(event, db)
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result.title == "Python Meetup"
    assert result.capacity == 50


def test_create_event_with_past_date_raises_400(sample_event_dict):
    db = fake_db()
    event = make_event(sample_event_dict, {"date": past_date()})
    with pytest.raises(HTTPException) as error:
        create_event(event, db)
    assert error.value.status_code == 400
    db.add.assert_not_called()


def test_list_events_without_filters_returns_all(prepopulated_event_store):
    db = fake_db(rows=prepopulated_event_store)
    result = list_events(search=None, location=None, title=None, db=db)
    assert len(result) == 3


def test_list_events_with_search_uses_database_filter(prepopulated_event_store):
    db = fake_db(rows=prepopulated_event_store)
    result = list_events(search="py", location=None, title=None, db=db)
    db.query.return_value.filter.assert_called_once()
    assert len(result) == 3


def test_list_events_filters_by_location(prepopulated_event_store):
    db = fake_db(rows=prepopulated_event_store)
    result = list_events(search=None, location="ALGIERS", title=None, db=db)
    assert len(result) == 2


def test_list_events_filters_by_title(prepopulated_event_store):
    db = fake_db(rows=prepopulated_event_store)
    result = list_events(search=None, location=None, title="workshop", db=db)
    assert [e.title for e in result] == ["Security Workshop"]


def test_list_events_filters_by_location_and_title(prepopulated_event_store):
    db = fake_db(rows=prepopulated_event_store)
    result = list_events(search=None, location="algiers", title="devops", db=db)
    assert [e.title for e in result] == ["DevOps Day"]


def test_get_event_returns_event():
    existing = SimpleNamespace(id=1, title="Found")
    db = fake_db(first=existing)
    assert get_event(1, db) is existing


def test_get_missing_event_raises_404():
    db = fake_db(first=None)
    with pytest.raises(HTTPException) as error:
        get_event(999, db)
    assert error.value.status_code == 404


def test_update_event_changes_fields(sample_event_dict):
    existing = SimpleNamespace(
        id=1, title="Old", description=None,
        date=future_date(), location="Old place", capacity=5,
    )
    db = fake_db(first=existing)
    new_data = EventUpdate.model_validate(
        event_payload(sample_event_dict, {"title": "New Title", "date": future_date()})
    )
    result = update_event(1, new_data, db)
    assert result is existing
    assert existing.title == "New Title"
    assert existing.capacity == 50
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(existing)


def test_update_missing_event_raises_404(sample_event_dict):
    db = fake_db(first=None)
    new_data = EventUpdate.model_validate(
        event_payload(sample_event_dict, {"date": future_date()})
    )
    with pytest.raises(HTTPException) as error:
        update_event(999, new_data, db)
    assert error.value.status_code == 404


def test_update_event_with_past_date_raises_400(sample_event_dict):
    existing = SimpleNamespace(id=1, title="Old")
    db = fake_db(first=existing)
    new_data = EventUpdate.model_validate(
        event_payload(sample_event_dict, {"date": past_date()})
    )
    with pytest.raises(HTTPException) as error:
        update_event(1, new_data, db)
    assert error.value.status_code == 400
    db.commit.assert_not_called()


def test_delete_event_removes_and_commits():
    existing = SimpleNamespace(id=1)
    db = fake_db(first=existing)
    assert delete_event(1, db) is None
    db.delete.assert_called_once_with(existing)
    db.commit.assert_called_once()


def test_delete_missing_event_raises_404():
    db = fake_db(first=None)
    with pytest.raises(HTTPException) as error:
        delete_event(999, db)
    assert error.value.status_code == 404
    db.delete.assert_not_called()