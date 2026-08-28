from types import SimpleNamespace
from unittest.mock import MagicMock

from app.agents.knowledge import KnowledgeAgent


def test_general_search_does_not_use_rag(monkeypatch):
    web_search = MagicMock()
    web_search.search.return_value = [
        {
            "title": "Exchange rate",
            "url": "https://example.com/rate",
            "content": "One euro is worth two units.",
        }
    ]
    agent = KnowledgeAgent(web_search_provider=web_search)
    monkeypatch.setattr(
        agent.client.responses,
        "create",
        MagicMock(return_value=SimpleNamespace(output_text="The rate is two units.")),
    )
    retrieve = MagicMock(side_effect=AssertionError("RAG must not be used"))
    monkeypatch.setattr(agent.retriever, "retrieve", retrieve)

    result = agent.handle_general_search("What is the exchange rate?", "user-1")

    assert result == (
        "The rate is two units.\n\n"
        "Sources:\n- https://example.com/rate"
    )
    web_search.search.assert_called_once_with(
        "What is the exchange rate?",
        max_results=5,
    )
    retrieve.assert_not_called()