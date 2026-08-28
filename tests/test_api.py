from fastapi.testclient import TestClient

from app.agents.router import AgentType
from app.main import app, router_agent


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_routes_to_knowledge(monkeypatch):
    monkeypatch.setattr(
        router_agent,
        "route",
        lambda message: AgentType.KNOWLEDGE,
    )

    response = client.post(
        "/chat",
        json={
            "message": "What's the difference between Get Classica and Get Smart?",
            "user_id": "cliente1988",
        },
    )

    assert response.status_code == 200
    assert response.json()["agent"] == "knowledge"

def test_chat_routes_to_customer_support(monkeypatch):
    monkeypatch.setattr(
        router_agent,
        "route",
        lambda message: AgentType.CUSTOMER_SUPPORT,
    )

    response = client.post(
        "/chat",
        json={
            "message": "My transaction was declined.",
            "user_id": "cliente1988",
        },
    )

    assert response.status_code == 200
    assert response.json()["agent"] == "customer_support"