
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def sample_event_dict():
    return {
        "title": "Python Developer Meetup",
        "description": "An introductory session on FastAPI and async programming.",
        "date": "2026-11-01",
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
        {"id": 1, "title": "FastAPI Masterclass", "location": "Algiers", "capacity": 100},
        {"id": 2, "title": "Cybersecurity Briefing", "location": "Oran", "capacity": 25},
        {"id": 3, "title": "Python Workshop", "location": "Online", "capacity": 50},
    ])
    return mock_event_store


@pytest.fixture(autouse=True)
def global_environment_logger():
    print("\n[SETUP] Running test...")
    yield
    print("[TEARDOWN] Test completed.")


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
