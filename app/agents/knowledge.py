from openai import OpenAI

from app.config import settings
from app.rag.retriever import KnowledgeRetriever


class KnowledgeAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.retriever = KnowledgeRetriever()

    def handle(self, message: str, user_id: str) -> str:
        documents = self.retriever.retrieve(
            message,
            top_k=5,
        )

        context_parts = []
        sources = []

        for index, document in enumerate(documents, start=1):
            source = document["source"]

            context_parts.append(
                f"[SOURCE {index}]\n"
                f"Title: {document['title']}\n"
                f"URL: {source}\n"
                f"Content:\n{document['text']}"
            )

            if source not in sources:
                sources.append(source)

        context = "\n\n".join(context_parts)

        response = self.client.responses.create(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are the Getnet Knowledge Agent. "
                        "Answer questions about Getnet products and services "
                        "using only the retrieved Getnet documentation provided below.\n\n"

                        "GROUNDING RULES:\n"
                        "- Use only facts supported by the retrieved context.\n"
                        "- Do not rely on prior knowledge about Getnet.\n"
                        "- Do not invent prices, rates, features, policies, "
                        "timelines, eligibility rules, or product capabilities.\n"
                        "- If the retrieved documentation is insufficient, "
                        "say that you could not find enough information in the "
                        "available Getnet documentation.\n"
                        "- Clearly distinguish products when comparing them.\n"
                        "- Keep the answer concise and useful.\n"
                        "- Do not invent URLs.\n"
                        "- Do not offer to search the web unless a web search tool is actually available.\n"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Customer question:\n{message}\n\n"
                        f"Retrieved Getnet documentation:\n\n{context}"
                    ),
                },
            ],
        )

        answer = response.output_text

        if sources:
            answer += "\n\nSources:\n"
            answer += "\n".join(
                f"- {source}"
                for source in sources[:3]
            )

        return answer