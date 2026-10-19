
def test_create_event_api(client, sample_event_dict):
    response = client.post("/events/", json=sample_event_dict)

    assert response.status_code == 201
    assert response.json()["title"] == sample_event_dict["title"]


def test_create_event_with_past_date_api(client, sample_event_dict):
    event_data = sample_event_dict.copy()
    event_data["date"] = "2020-01-01"

    response = client.post("/events/", json=event_data)

    assert response.status_code == 400


def test_list_events_api(client, sample_event_dict):
    client.post("/events/", json=sample_event_dict)

    response = client.get("/events/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_events_by_search_api(client, sample_event_dict):
    client.post("/events/", json=sample_event_dict)

    response = client.get("/events/?search=Python")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_events_by_location_api(client, sample_event_dict):
    client.post("/events/", json=sample_event_dict)

    response = client.get("/events/?location=Online")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_events_by_title_api(client, sample_event_dict):
    client.post("/events/", json=sample_event_dict)

    response = client.get("/events/?title=Developer")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_event_api(client, sample_event_dict):
    create_response = client.post("/events/", json=sample_event_dict)
    event_id = create_response.json()["id"]

    response = client.get(f"/events/{event_id}")

    assert response.status_code == 200
    assert response.json()["id"] == event_id


def test_get_missing_event_api(client):
    response = client.get("/events/99999")

    assert response.status_code == 404


def test_update_event_api(client, sample_event_dict):
    create_response = client.post("/events/", json=sample_event_dict)
    event_id = create_response.json()["id"]

    updated_data = sample_event_dict.copy()
    updated_data["title"] = "Updated Python Workshop"

    response = client.put(f"/events/{event_id}", json=updated_data)

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Python Workshop"


def test_update_missing_event_api(client, sample_event_dict):
    response = client.put("/events/99999", json=sample_event_dict)

    assert response.status_code == 404


def test_update_event_with_past_date_api(client, sample_event_dict):
    create_response = client.post("/events/", json=sample_event_dict)
    event_id = create_response.json()["id"]

    updated_data = sample_event_dict.copy()
    updated_data["date"] = "2020-01-01"

    response = client.put(f"/events/{event_id}", json=updated_data)

    assert response.status_code == 400


def test_delete_event_api(client, sample_event_dict):
    create_response = client.post("/events/", json=sample_event_dict)
    event_id = create_response.json()["id"]

    response = client.delete(f"/events/{event_id}")

    assert response.status_code == 204
    assert client.get(f"/events/{event_id}").status_code == 404


def test_delete_missing_event_api(client):
    response = client.delete("/events/99999")

    assert response.status_code == 404
