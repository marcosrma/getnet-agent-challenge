import json

from openai import OpenAI

from app.config import settings
from app.tools.customer import (
    get_customer_profile,
    get_settlement_schedule,
    get_terminal_status,
)


TOOLS = [
    {
        "type": "function",
        "name": "get_customer_profile",
        "description": "Retrieve basic customer profile information.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
            },
            "required": ["user_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_settlement_schedule",
        "description": (
            "Retrieve settlement and expected deposit information "
            "for a customer's recent sales."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
            },
            "required": ["user_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_terminal_status",
        "description": (
            "Retrieve the current card terminal status for a customer."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
            },
            "required": ["user_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


TOOL_FUNCTIONS = {
    "get_customer_profile": get_customer_profile,
    "get_settlement_schedule": get_settlement_schedule,
    "get_terminal_status": get_terminal_status,
}


class CustomerSupportAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def handle(self, message: str, user_id: str) -> str:
        input_messages = [
            {
                "role": "system",
                "content": (
                    "You are a Getnet customer support agent. "
                    "Use the available tools whenever customer-specific information is needed. "

                    "STRICT GROUNDING RULES:\n"
                    "- Answer only with facts contained in the user's message or returned by tools.\n"
                    "- Never invent customer data, procedures, policies, timelines, troubleshooting steps, "
                    "or operational capabilities.\n"
                    "- Never claim that you opened a ticket, escalated a case, scheduled a technician, "
                    "changed an account, issued a refund, or performed any action unless a tool actually "
                    "performed that action.\n"
                    "- If the available tools do not provide enough information, explicitly say so.\n"
                    "- Keep responses concise and factual.\n"

                    "The authenticated user_id is authoritative. "
                    "Never access another customer's data."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Authenticated user_id: {user_id}\n"
                    f"Customer message: {message}"
                ),
            },
        ]

        response = self.client.responses.create(
            model=settings.openai_model,
            input=input_messages,
            tools=TOOLS,
        )

        tool_outputs = []

        for item in response.output:
            if item.type != "function_call":
                continue

            function = TOOL_FUNCTIONS.get(item.name)

            if function is None:
                continue

            arguments = json.loads(item.arguments)

            # Security guardrail:
            # never allow the LLM to substitute another customer's ID.
            arguments["user_id"] = user_id

            result = function(**arguments)

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result),
                }
            )

        if not tool_outputs:
            return response.output_text

        final_response = self.client.responses.create(
            model=settings.openai_model,
            previous_response_id=response.id,
            input=tool_outputs,
        )

        return final_response.output_text