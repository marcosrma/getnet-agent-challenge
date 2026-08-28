from fastapi import FastAPI

from app.agents.customer_support import CustomerSupportAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.router import AgentType, RouterAgent
from app.guardrails import check_message
from app.models.schemas import ChatRequest, ChatResponse


app = FastAPI(
    title="Getnet Multi-Agent Support System",
    version="0.1.0",
)

router_agent = RouterAgent()
knowledge_agent = KnowledgeAgent()
customer_support_agent = CustomerSupportAgent()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    guardrail_result = check_message(request.message)

    if not guardrail_result.allowed:
        return ChatResponse(
            response=guardrail_result.reason or "Não posso atender a essa solicitação.",
            agent="guardrails",
        )

    selected_agent = router_agent.route(request.message)

    if selected_agent == AgentType.CUSTOMER_SUPPORT:
        response = customer_support_agent.handle(
            request.message,
            request.user_id,
        )
    elif selected_agent == AgentType.GENERAL_SEARCH:
        response = knowledge_agent.handle_general_search(
            request.message,
            request.user_id,
        )
    else:
        response = knowledge_agent.handle(
            request.message,
            request.user_id,
        )

    return ChatResponse(
        response=response,
        agent=selected_agent.value,
    )