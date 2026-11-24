import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def future_date(days=30):
    return (date.today() + timedelta(days=days)).isoformat()

def test_create_and_fetch_event_integration():
    response = client.post("/events/", json={
        "title": "DevOps Integration Conf", "location": "Constantine",
        "date": future_date(), "capacity": 200})
    assert response.status_code == 201, response.text
    event_id = response.json()["id"]

    get_resp = client.get(f"/events/{event_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "DevOps Integration Conf"

def test_register_participant_to_event_integration():
    e_resp = client.post("/events/", json={
        "title": "Cybersecurity Workshop", "location": "NTIC",
        "date": future_date(), "capacity": 50})
    assert e_resp.status_code == 201, e_resp.text
    event_id = e_resp.json()["id"]

    p_resp = client.post("/participants/", json={
        "name": "Alice Dev",
        "email": f"alice_{uuid.uuid4().hex[:8]}@example.com"})
    assert p_resp.status_code == 201
    part_id = p_resp.json()["id"]

    reg_resp = client.post(f"/events/{event_id}/register/{part_id}")
    assert reg_resp.status_code == 201

    list_resp = client.get(f"/events/{event_id}/participants")
    assert list_resp.status_code == 200
    assert any(p["id"] == part_id for p in list_resp.json())

def test_register_non_existent_event_returns_404():
    assert client.post("/events/9999/register/1").status_code == 404