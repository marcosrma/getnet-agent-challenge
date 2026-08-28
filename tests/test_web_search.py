import pytest
from unittest.mock import MagicMock

from app.tools.web_search import WebSearchProvider


def test_web_search_propagates_tavily_failure():
    client = MagicMock()
    client.search.side_effect = RuntimeError("Tavily unavailable")

    with pytest.raises(RuntimeError, match="Tavily unavailable"):
        WebSearchProvider(client=client).search("weather")


def test_web_search_uses_tavily_and_normalizes_results():
    client = MagicMock()
    client.search.return_value = {
        "results": [
            {
                "title": "Weather",
                "url": "https://example.com/weather",
                "content": "Sunny",
                "score": 0.9,
            }
        ]
    }

    results = WebSearchProvider(client=client).search("weather", max_results=3)

    client.search.assert_called_once_with(
        query="weather",
        search_depth="advanced",
        max_results=3,
        include_answer=False,
    )
    assert results == [
        {
            "title": "Weather",
            "url": "https://example.com/weather",
            "content": "Sunny",
        }
    ]