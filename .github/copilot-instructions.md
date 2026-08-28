# Project Instructions

This repository implements the Getnet Multi-Agent Support System challenge.

Architecture:
- FastAPI API
- RouterAgent
- KnowledgeAgent with RAG over Getnet content
- CustomerSupportAgent with tools
- General search via web search tool
- OpenAI for routing/generation/embeddings
- ChromaDB for vector storage
- pytest for tests

Engineering rules:
- Keep code modular and simple.
- Do not introduce unnecessary infrastructure.
- Do not make real external API calls in unit tests.
- Mock OpenAI and web-search providers in tests.
- Preserve existing behavior unless explicitly changing it.
- Run pytest after modifications.
- Do not commit or push unless asked.
- Prefer grounded answers and explicit guardrails.
- Read CHALLENGE.md before making architectural changes.