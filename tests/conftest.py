import pytest

from app.schemas import EventCreate


@pytest.fixture
def sample_event_dict():
    return {
        "title": "Python Developer Meetup",
        "description": "An introductory session on FastAPI and async programming.",
        "date": "2026-12-01",
        "location": "Online",
        "capacity": 50,
    }


@pytest.fixture
def sample_participant_dict():
    return {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
    }


@pytest.fixture
def mock_event_store():
    store = []
    yield store
    store.clear()


@pytest.fixture
def prepopulated_event_store(mock_event_store):
    mock_event_store.extend([
        EventCreate(title="FastAPI Masterclass", date="2026-11-01", location="Algiers", capacity=100),
        EventCreate(title="Cybersecurity Briefing", date="2026-11-15", location="Oran", capacity=25),
        EventCreate(title="Python Workshop", date="2026-12-01", location="Online", capacity=50),
    ])
    return mock_event_store


@pytest.fixture(autouse=True)
def global_environment_logger():
    print("\n[SETUP] Running test...")
    yield
    print("[TEARDOWN] Test completed.")