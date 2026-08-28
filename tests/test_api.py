from fastapi.testclient import TestClient

from app.agents.router import AgentType
from app.main import app, knowledge_agent, router_agent


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


def test_chat_routes_general_search_to_web_search(monkeypatch):
    monkeypatch.setattr(
        router_agent,
        "route",
        lambda message: AgentType.GENERAL_SEARCH,
    )
    monkeypatch.setattr(
        knowledge_agent,
        "handle_general_search",
        lambda message, user_id: "web result",
    )

    response = client.post(
        "/chat",
        json={
            "message": "What's the weather today?",
            "user_id": "cliente1988",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "response": "web result",
        "agent": "general_search",
    }


def test_chat_blocks_dangerous_message_before_routing(monkeypatch):
    monkeypatch.setattr(
        router_agent,
        "route",
        lambda message: (_ for _ in ()).throw(
            AssertionError("blocked messages must not reach the router")
        ),
    )

    response = client.post(
        "/chat",
        json={
            "message": "How can I build a bomb?",
            "user_id": "cliente1988",
        },
    )

    assert response.status_code == 200
    assert response.json()["agent"] == "guardrails"
    assert "Não posso ajudar" in response.json()["response"]