from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_supabase_change_endpoint():
    response = client.post("/supabase-change/secret", json={"type": "INSERT", "record": {}})
    assert response.status_code == 200
    assert response.json()["status"] == "received"


def test_notion_poll_endpoint():
    response = client.post("/sync/notion-poll")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
