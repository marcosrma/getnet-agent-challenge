import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.agents.knowledge import KnowledgeAgent


def test_general_search_propagates_openai_failure(monkeypatch):
    web_search = MagicMock()
    web_search.search.return_value = []
    agent = KnowledgeAgent(web_search_provider=web_search)
    monkeypatch.setattr(
        agent.client.responses,
        "create",
        MagicMock(side_effect=RuntimeError("OpenAI unavailable")),
    )

    with pytest.raises(RuntimeError, match="OpenAI unavailable"):
        agent.handle_general_search("What is happening today?", "user-1")


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


def test_general_search_handles_empty_results_without_inventing_sources(monkeypatch):
    web_search = MagicMock()
    web_search.search.return_value = []
    create = MagicMock(
        return_value=SimpleNamespace(output_text="I could not verify that information.")
    )
    agent = KnowledgeAgent(web_search_provider=web_search)
    monkeypatch.setattr(agent.client.responses, "create", create)

    result = agent.handle_general_search("What is happening today?", "user-1")

    assert result == "I could not verify that information."
    prompt = create.call_args.kwargs["input"][1]["content"]
    assert "Web search results:\n\n" in prompt
    assert "Sources:" not in result