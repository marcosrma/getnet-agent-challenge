from unittest.mock import MagicMock

from app.agents.router import AgentType, RouterAgent


def test_router_uses_llm_for_knowledge(monkeypatch):
    router = RouterAgent()

    fake_response = MagicMock()
    fake_response.output_parsed.agent = AgentType.KNOWLEDGE

    monkeypatch.setattr(
        router.client.responses,
        "parse",
        MagicMock(return_value=fake_response),
    )

    result = router.route(
        "What's the difference between Get Classica and Get Smart?"
    )

    assert result == AgentType.KNOWLEDGE


def test_router_uses_llm_for_customer_support(monkeypatch):
    router = RouterAgent()

    fake_response = MagicMock()
    fake_response.output_parsed.agent = AgentType.CUSTOMER_SUPPORT

    monkeypatch.setattr(
        router.client.responses,
        "parse",
        MagicMock(return_value=fake_response),
    )

    result = router.route(
        "When will the money from yesterday's sales be deposited?"
    )

    assert result == AgentType.CUSTOMER_SUPPORT

def test_router_falls_back_when_llm_fails(monkeypatch):
    router = RouterAgent()

    monkeypatch.setattr(
        router.client.responses,
        "parse",
        MagicMock(side_effect=Exception("API unavailable")),
    )

    result = router.route(
        "My transaction was declined."
    )

    assert result == AgentType.CUSTOMER_SUPPORT

def test_router_uses_llm_for_general_search(monkeypatch):
    router = RouterAgent()

    fake_response = MagicMock()
    fake_response.output_parsed.agent = AgentType.GENERAL_SEARCH

    monkeypatch.setattr(
        router.client.responses,
        "parse",
        MagicMock(return_value=fake_response),
    )

    result = router.route(
        "What's the weather forecast in Porto Alegre tomorrow?"
    )

    assert result == AgentType.GENERAL_SEARCH

def test_router_fallback_routes_general_question_to_search(monkeypatch):
    router = RouterAgent()

    monkeypatch.setattr(
        router.client.responses,
        "parse",
        MagicMock(side_effect=Exception("API unavailable")),
    )

    result = router.route(
        "What's the euro exchange rate today?"
    )

    assert result == AgentType.GENERAL_SEARCH


def test_router_fallback_routes_handoff_request_to_human(monkeypatch):
    router = RouterAgent()

    monkeypatch.setattr(
        router.client.responses,
        "parse",
        MagicMock(side_effect=Exception("API unavailable")),
    )

    result = router.route("I want to speak with a human agent")

    assert result == AgentType.HUMAN_HANDOFF