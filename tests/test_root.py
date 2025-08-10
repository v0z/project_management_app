from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_server_is_up():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "server is up"}
