from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    user_id: str = Field(min_length=1)


class ChatResponse(BaseModel):
    response: str
    agent: str