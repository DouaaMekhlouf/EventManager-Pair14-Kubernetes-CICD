"""Student A - Event schema & search unit tests."""
import pytest
from pydantic import ValidationError

from app.schemas import EventCreate  # adjust to your project
from app.search import filter_events_by_location, filter_events_by_title


def make_event(base: dict, **overrides) -> EventCreate:
    return EventCreate(**{**base, **overrides})


# ======================= HAPPY PATH (2+) =======================
def test_valid_event_creation(sample_event_dict):
    event = EventCreate(**sample_event_dict)
    assert event.title == "Python Meetup"
    assert event.capacity == 50


def test_filter_events_by_location_case_insensitive(prepopulated_event_store):
    result = filter_events_by_location(prepopulated_event_store, "ALGIERS")
    assert len(result) == 2  # "Algiers" and "algiers"


def test_filter_events_by_title_case_insensitive(prepopulated_event_store):
    result = filter_events_by_title(prepopulated_event_store, "python")
    assert len(result) == 1
    assert result[0].title == "Python Meetup"


def test_filter_events_no_match_returns_empty(prepopulated_event_store):
    assert filter_events_by_location(prepopulated_event_store, "Paris") == []


# ======================= BOUNDARY VALUES (3+) =======================
def test_capacity_minimum_boundary(sample_event_dict):
    assert make_event(sample_event_dict, capacity=1).capacity == 1


def test_capacity_maximum_boundary(sample_event_dict):
    assert make_event(sample_event_dict, capacity=10_000).capacity == 10_000


def test_title_length_minimum_boundary(sample_event_dict):
    assert make_event(sample_event_dict, title="abc").title == "abc"


# ======================= NEGATIVE TESTS (2+) =======================
@pytest.mark.parametrize("short_title", ["", "a", "ab"])
def test_title_too_short_raises(sample_event_dict, short_title):
    with pytest.raises(ValidationError):
        make_event(sample_event_dict, title=short_title)


@pytest.mark.parametrize("bad_capacity", [0, -1, -100, 10_001])
def test_capacity_out_of_bounds_raises(sample_event_dict, bad_capacity):
    with pytest.raises(ValidationError):
        make_event(sample_event_dict, capacity=bad_capacity)