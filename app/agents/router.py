from enum import Enum


class AgentType(str, Enum):
    KNOWLEDGE = "knowledge"
    CUSTOMER_SUPPORT = "customer_support"


class RouterAgent:
    def route(self, message: str) -> AgentType:
        text = message.lower()

        support_keywords = [
            "my ",
            "mine",
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