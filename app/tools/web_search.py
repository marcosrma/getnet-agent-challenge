from tavily import TavilyClient

from app.config import settings


class WebSearchProvider:
	def __init__(self, client=None):
		self.client = client or TavilyClient(api_key=settings.tavily_api_key)

	def search(self, query: str, max_results: int = 5) -> list[dict]:
		response = self.client.search(
			query=query,
			search_depth="advanced",
			max_results=max_results,
			include_answer=False,
		)

		return [
			{
				"title": result.get("title", ""),
				"url": result.get("url", ""),
				"content": result.get("content", ""),
			}
			for result in response.get("results", [])
		]


def search_web(query: str, max_results: int = 5) -> list[dict]:
	return WebSearchProvider().search(query, max_results=max_results)
