import pytest
from pydantic import ValidationError

from app.schemas import EventCreate
from app.search import filter_events_by_location, filter_events_by_title


# ---------- Happy path ----------
def test_valid_event_creation(sample_event_dict):
    event = EventCreate(**sample_event_dict)
    assert event.title == "Python Developer Meetup"
    assert event.capacity == 50


def test_filter_by_location_case_insensitive(prepopulated_event_store):
    result = filter_events_by_location(prepopulated_event_store, "ALGIERS")
    assert len(result) == 1
    assert result[0].location == "Algiers"


def test_filter_by_title_case_insensitive(prepopulated_event_store):
    result = filter_events_by_title(prepopulated_event_store, "PYTHON")
    assert len(result) == 1
    assert result[0].title == "Python Workshop"


# ---------- Boundary values ----------
def test_capacity_minimum_boundary(sample_event_dict):
    sample_event_dict["capacity"] = 1
    assert EventCreate(**sample_event_dict).capacity == 1


def test_capacity_maximum_boundary(sample_event_dict):
    sample_event_dict["capacity"] = 10_000
    assert EventCreate(**sample_event_dict).capacity == 10_000


def test_title_length_exactly_three(sample_event_dict):
    sample_event_dict["title"] = "abc"
    assert len(EventCreate(**sample_event_dict).title) == 3


# ---------- Negative ----------
def test_title_too_short_raises(sample_event_dict):
    sample_event_dict["title"] = "ab"
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


@pytest.mark.parametrize("bad_capacity", [0, -1, 10_001])
def test_invalid_capacity_raises(sample_event_dict, bad_capacity):
    sample_event_dict["capacity"] = bad_capacity
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


def test_missing_date_raises(sample_event_dict):
    del sample_event_dict["date"]
    with pytest.raises(ValidationError):
        EventCreate(**sample_event_dict)


# ---------- Extra filter coverage ----------
def test_filter_no_match_returns_empty(prepopulated_event_store):
    assert filter_events_by_location(prepopulated_event_store, "Paris") == []