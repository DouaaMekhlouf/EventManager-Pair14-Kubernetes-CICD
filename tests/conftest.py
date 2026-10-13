import pytest

@pytest.fixture
def sample_event_dict():
    return {
        "title": "Python Developer Meetup",
        "description": "An introductory session on FastAPI and async programming.",
        "location": "Online",
        "capacity": 50
    }

@pytest.fixture
def sample_participant_dict():
    return {
        "name": "Jane Doe",
        "email": "jane.doe@example.com"
    }

@pytest.fixture
def mock_event_store():
    store = []
    yield store
    store.clear()

@pytest.fixture
def prepopulated_event_store(mock_event_store):
    mock_event_store.extend([
        {"id": 1, "title": "FastAPI Masterclass", "location": "Algiers", "capacity": 100},
        {"id": 2, "title": "Cybersecurity Briefing", "location": "Oran", "capacity": 25},
        {"id": 3, "title": "Python Workshop", "location": "Online", "capacity": 50}
    ])
    return mock_event_store

@pytest.fixture(autouse=True)
def global_environment_logger():
    print("\n[SETUP] Running test...")
    yield
    print("[TEARDOWN] Test completed.")