# Getnet Multi-Agent Support System

Sistema de suporte multiagente para o desafio Getnet. A aplicação expõe uma
API FastAPI e usa OpenAI, ChromaDB e Tavily para responder perguntas com
roteamento especializado e grounding explícito.

## Requisitos

- Python 3.12 ou superior
- Docker e Docker Compose (opcional)
- `OPENAI_API_KEY`
- `TAVILY_API_KEY` para perguntas de busca geral

## Configuração local

```bash
cp .env.example .env
```

Preencha `OPENAI_API_KEY` e `TAVILY_API_KEY` no arquivo `.env`.

Instale o projeto e as dependências:

```bash
python -m pip install .
```

## Base de conhecimento

A base RAG é criada a partir de páginas públicas do site Getnet. O processo
baixa as páginas, extrai o texto, divide o conteúdo em chunks, gera embeddings
com OpenAI e grava os vetores no ChromaDB em `data/chroma`.

Execute a ingestão antes do primeiro uso da API:

```bash
python -m app.rag.ingest
```

O processo requer acesso à internet e consome chamadas da API de embeddings.
Execute-o novamente quando quiser atualizar o conteúdo indexado.

## Executar a API

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em `http://localhost:8000`. O endpoint de healthcheck
é `GET /health`.

Exemplo de conversa:

```bash
curl -X POST http://localhost:8000/chat \
	-H 'Content-Type: application/json' \
	-d '{"message":"Qual a diferença entre Get Clássica e Get Smart?","user_id":"cliente1988"}'
```

Resposta:

```json
{
	"response": "...",
	"agent": "knowledge"
}
```

O campo `agent` identifica a rota escolhida: `knowledge`, `customer_support`
ou `general_search`.

## Executar com Docker

Configure o `.env` conforme descrito acima. Em uma instalação limpa, primeiro
construa a imagem e execute a ingestão usando o volume persistente:

```bash
docker compose build
docker compose run --rm api python -m app.rag.ingest
docker compose up
```

Depois acesse `http://localhost:8000`. O Compose expõe a porta `8000` e monta
`./data/chroma` em `/app/data/chroma`, preservando a base vetorial entre
reinicializações. Para executar em segundo plano:

```bash
docker compose up -d
```

## Arquitetura

O fluxo de uma mensagem é:

```text
POST /chat
		|
		v
RouterAgent (OpenAI Structured Output)
		|
		+--> knowledge        --> KnowledgeAgent --> Retriever --> ChromaDB --> OpenAI
		|
		+--> general_search   --> KnowledgeAgent --> Tavily --> OpenAI
		|
		+--> customer_support --> CustomerSupportAgent --> ferramentas locais --> OpenAI
```

### RouterAgent

Classifica cada mensagem em exatamente um destino. Se a chamada ao modelo
falhar, usa uma classificação local por palavras-chave como fallback.

### KnowledgeAgent

Para `knowledge`, consulta exclusivamente o retriever sobre a documentação
Getnet indexada e instrui o modelo a responder apenas com esse contexto. Essa
rota não usa busca na internet.

Para `general_search`, consulta o `WebSearchProvider`, que usa Tavily, e envia
os resultados ao modelo para síntese fundamentada. As URLs encontradas são
incluídas como fontes na resposta.

### CustomerSupportAgent

Atende questões específicas do cliente usando chamadas de ferramentas. As
ferramentas disponíveis são:

- `get_customer_profile`
- `get_settlement_schedule`
- `get_terminal_status`

O `user_id` autenticado é sempre aplicado pelo servidor antes da execução da
ferramenta, impedindo que o modelo consulte dados de outro cliente.

## Testes

Execute:

```bash
pytest -v
```

Os testes cobrem o endpoint, o roteador, o agente de suporte, as ferramentas
de cliente, o fluxo RAG/web do agente de conhecimento e a normalização dos
resultados do Tavily. Chamadas OpenAI e Tavily são substituídas por mocks; a
suíte não depende de credenciais nem faz chamadas externas.

Uma estratégia de integração em ambiente controlado deve validar o fluxo
completo usando um banco Chroma temporário, respostas determinísticas dos
providers e cenários representativos das três rotas. Em produção, também é
recomendável observar latência, erros por provider, taxa de fallback do router,
qualidade de grounding e presença de fontes nas respostas.
