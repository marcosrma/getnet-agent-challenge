from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat():
    response = client.post(
        "/chat",
        json={
            "message": "What's the difference between Get Classica and Get Smart?",
            "user_id": "cliente1988",
        },
    )

    assert response.status_code == 200
    assert response.json()["agent"] == "router"
    assert "Received:" in response.json()["response"]