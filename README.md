# getnet-agent-challenge
Agent Orchestration Challenge

## Configuração

Copie `.env.example` para `.env` e defina `OPENAI_API_KEY` e `TAVILY_API_KEY`.

Perguntas sobre Getnet continuam sendo roteadas para o `KnowledgeAgent` com
RAG. Perguntas gerais são roteadas para o mesmo agente, mas usam o provider
Tavily para buscar fontes atuais antes da geração da resposta. Perguntas
específicas do cliente continuam sendo tratadas pelo `CustomerSupportAgent`.

## Testes

Execute `pytest -v`. Os testes substituem as chamadas OpenAI e Tavily por
mocks e não fazem chamadas externas.
