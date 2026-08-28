from enum import Enum

from openai import OpenAI
from pydantic import BaseModel

from app.config import settings


class AgentType(str, Enum):
    KNOWLEDGE = "knowledge"
    CUSTOMER_SUPPORT = "customer_support"


class RoutingDecision(BaseModel):
    agent: AgentType


class RouterAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def route(self, message: str) -> AgentType:
        try:
            response = self.client.responses.parse(
                model=settings.openai_model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are the routing agent for a Getnet customer support system. "
                            "Route each message to exactly one specialized agent.\n\n"
                            "knowledge: questions about Getnet products, services, features, "
                            "policies, general information, or general-purpose questions.\n\n"
                            "customer_support: requests that depend on the specific customer's "
                            "account, transactions, settlements, card machine status, errors, "
                            "or other customer-specific operational data."
                        ),
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
                text_format=RoutingDecision,
            )

            return response.output_parsed.agent

        except Exception:
            return self._fallback_route(message)

    def _fallback_route(self, message: str) -> AgentType:
        text = message.lower()

        support_keywords = [
            "my ",
            "yesterday's sales",
            "deposit",
            "transaction",
            "decline",
            "won't connect",
            "not connect",
            "card machine",
            "terminal",
        ]

        if any(keyword in text for keyword in support_keywords):
            return AgentType.CUSTOMER_SUPPORT

        return AgentType.KNOWLEDGE