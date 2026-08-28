from enum import Enum

from openai import OpenAI
from pydantic import BaseModel

from app.config import settings


class AgentType(str, Enum):
    KNOWLEDGE = "knowledge"
    CUSTOMER_SUPPORT = "customer_support"
    GENERAL_SEARCH = "general_search"


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
                        "Route each user message to exactly one specialized destination.\n\n"

                        "knowledge:\n"
                        "- Questions about Getnet products, services, features, fees, "
                        "policies, payment solutions, Pix, receivables, Payment Link, "
                        "card machines, or other Getnet information.\n\n"

                        "customer_support:\n"
                        "- Requests that require data about the specific authenticated customer, "
                        "such as their transactions, settlements, deposits, terminal status, "
                        "account data, or customer-specific operational issues.\n\n"

                        "general_search:\n"
                        "- General-purpose questions that are not about Getnet and may require "
                        "current external information, such as weather, exchange rates, news, "
                        "or other web information.\n\n"

                        "Return exactly one destination."
                    ),
                    },                    {
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

        getnet_keywords = [
            "getnet",
            "get classica",
            "get clássica",
            "get smart",
            "get mini",
            "payment link",
            "receivables",
            "antecipação",
            "crediário",
            "pix",
        ]

        if any(keyword in text for keyword in support_keywords):
            return AgentType.CUSTOMER_SUPPORT

        if any(keyword in text for keyword in getnet_keywords):
            return AgentType.KNOWLEDGE

        return AgentType.GENERAL_SEARCH