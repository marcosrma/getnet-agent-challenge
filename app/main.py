from fastapi import FastAPI

from app.models.schemas import ChatRequest, ChatResponse


app = FastAPI(
    title="Getnet Multi-Agent Support System",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(
        response=f"Received: {request.message}",
        agent="router",
    )