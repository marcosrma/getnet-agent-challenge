import time

from fastapi import FastAPI, Header, HTTPException
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.agents.customer_support import CustomerSupportAgent
from app.agents.handoff import HumanHandoffAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.router import AgentType, RouterAgent
from app.config import settings
from app.guardrails import check_message
from app.models.schemas import ChatRequest, ChatResponse
from app.observability import logger, record_chat_request


app = FastAPI(
    title="Getnet Multi-Agent Support System",
    version="0.1.0",
)

router_agent = RouterAgent()
knowledge_agent = KnowledgeAgent()
customer_support_agent = CustomerSupportAgent()
human_handoff_agent = HumanHandoffAgent()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    authenticated_user_id: str | None = Header(default=None, alias="X-User-ID"),
) -> ChatResponse:
    started_at = time.perf_counter()
    agent = "unknown"
    status = "error"

    try:
        if settings.require_user_authentication and not authenticated_user_id:
            raise HTTPException(
                status_code=401,
                detail="X-User-ID header is required.",
            )

        if authenticated_user_id and authenticated_user_id != request.user_id:
            raise HTTPException(
                status_code=403,
                detail="Authenticated user does not match user_id.",
            )

        guardrail_result = check_message(request.message)

        if not guardrail_result.allowed:
            agent = "guardrails"
            response = guardrail_result.reason or "Não posso atender a essa solicitação."
        else:
            selected_agent = router_agent.route(request.message)
            agent = selected_agent.value

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
            elif selected_agent == AgentType.HUMAN_HANDOFF:
                response = human_handoff_agent.handle(
                    request.message,
                    request.user_id,
                )
            else:
                response = knowledge_agent.handle(
                    request.message,
                    request.user_id,
                )

        status = "success"
        return ChatResponse(response=response, agent=agent)
    except Exception:
        logger.exception(
            "chat request failed",
            extra={
                "event": "chat_request_failed",
                "method": "POST",
                "path": "/chat",
                "status": status,
                "agent": agent,
            },
        )
        raise
    finally:
        record_chat_request(
            agent=agent,
            status=status,
            method="POST",
            path="/chat",
            started_at=started_at,
        )