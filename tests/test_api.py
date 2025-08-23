import mongomock
import pytest
from fastapi.testclient import TestClient
import src.people_service.main as main

@pytest.fixture(autouse=True)
def fake_db():
    client = mongomock.MongoClient()
    main.db = client["test_db"]
    yield

def get_client():
    return TestClient(main.app)

def test_health():
    r = get_client().get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_post_and_list():
    c = get_client()
    assert c.get("/items").json() == []
    r = c.post("/items", json={"name":"alpha"})
    assert r.status_code == 201
    data = r.json()
    assert data["ok"] is True and data["item"]["name"] == "alpha" and "id" in data["item"]
    items = c.get("/items").json()
    assert len(items) == 1 and items[0]["name"] == "alpha"

def test_delete_by_name_many():
    c = get_client()
    c.post("/items", json={"name":"dup"})
    c.post("/items", json={"name":"dup"})
    c.post("/items", json={"name":"other"})
    r = c.delete("/items/name/dup")
    assert r.status_code == 200 and r.json()["deleted"] == 2
    names = [i["name"] for i in c.get("/items").json()]
    assert names == ["other"]

def test_delete_by_id_one():
    c = get_client()
    item_id = c.post("/items", json={"name":"x"}).json()["item"]["id"]
    r = c.delete(f"/items/id/{item_id}")
    assert r.status_code == 200 and r.json()["deleted"] == 1
    assert c.get("/items").json() == []

def test_clear_all():
    c = get_client()
    c.post("/items", json={"name":"a"})
    c.post("/items", json={"name":"b"})
    r = c.delete("/items")
    assert r.status_code == 200 and r.json()["deleted"] == 2

def test_post_validation():
    c = get_client()
    assert c.post("/items", json={"name":""}).status_code == 400
