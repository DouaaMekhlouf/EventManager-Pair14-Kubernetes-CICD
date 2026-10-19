"""Shared fixtures for Lab 2 - no DB, no HTTP, everything in memory."""
import pytest

from app.schemas import EventCreate  # adjust to your project


# ---------- Data generators ----------
@pytest.fixture
def sample_event_dict():
    """A clean, valid event payload."""
    return {
        "title": "Python Meetup",
        "description": "Monthly community meetup",
        "location": "Algiers",
        "date": "2026-12-01",
        "capacity": 50,
    }


@pytest.fixture
def sample_participant_dict():
    """A clean, valid participant payload."""
    return {"name": "Amine Benali", "email": "amine@example.com"}


# ---------- State & teardown ----------
@pytest.fixture
def mock_event_store():
    """In-memory list repository; cleared after each test."""
    store = []
    yield store
    store.clear()


# ---------- Chained fixture ----------
@pytest.fixture
def prepopulated_event_store(mock_event_store, sample_event_dict):
    """mock_event_store pre-filled with 3 event objects."""
    variants = [
        ("Python Meetup", "Algiers"),
        ("Security Workshop", "Oran"),
        ("DevOps Day", "algiers"),  # lowercase on purpose (case-insensitivity)
    ]
    for title, location in variants:
        data = {**sample_event_dict, "title": title, "location": location}
        mock_event_store.append(EventCreate(**data))
    return mock_event_store


# ---------- Autouse ----------
@pytest.fixture(autouse=True)
def global_environment_logger(request):
    print(f"\n[SETUP] starting {request.node.name}")
    yield
    print(f"\n[TEARDOWN] finished {request.node.name}")