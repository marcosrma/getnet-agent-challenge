import json
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.agents.customer_support import CustomerSupportAgent


def test_customer_support_calls_settlement_tool(monkeypatch):
    agent = CustomerSupportAgent()

    first_response = SimpleNamespace(
        id="resp_1",
        output=[
            SimpleNamespace(
                type="function_call",
                name="get_settlement_schedule",
                arguments=json.dumps({"user_id": "cliente9999"}),
                call_id="call_1",
            )
        ],
        output_text="",
    )

    final_response = SimpleNamespace(
        output_text="Your funds are scheduled for 2026-08-28."
    )

    create_mock = MagicMock(
        side_effect=[first_response, final_response]
    )

    monkeypatch.setattr(
        agent.client.responses,
        "create",
        create_mock,
    )

    result = agent.handle(
        "When will yesterday's sales be deposited?",
        "cliente1988",
    )

    assert result == "Your funds are scheduled for 2026-08-28."
    assert create_mock.call_count == 2

    second_call = create_mock.call_args_list[1]

    tool_output = second_call.kwargs["input"][0]
    data = json.loads(tool_output["output"])

    assert data["user_id"] == "cliente1988"
    assert data["expected_deposit_date"] == "2026-08-28"

def test_customer_support_calls_terminal_tool(monkeypatch):
    agent = CustomerSupportAgent()

    first_response = SimpleNamespace(
        id="resp_2",
        output=[
            SimpleNamespace(
                type="function_call",
                name="get_terminal_status",
                arguments=json.dumps({"user_id": "cliente2001"}),
                call_id="call_2",
            )
        ],
        output_text="",
    )

    final_response = SimpleNamespace(
        output_text="Your terminal POS-99881 is currently offline."
    )

    create_mock = MagicMock(
        side_effect=[first_response, final_response]
    )

    monkeypatch.setattr(
        agent.client.responses,
        "create",
        create_mock,
    )

    result = agent.handle(
        "Is my card machine online?",
        "cliente2001",
    )

    assert result == "Your terminal POS-99881 is currently offline."
    assert create_mock.call_count == 2

    second_call = create_mock.call_args_list[1]
    tool_output = second_call.kwargs["input"][0]

    data = json.loads(tool_output["output"])

    assert data["id"] == "POS-99881"
    assert data["status"] == "offline"

def test_customer_support_returns_direct_response_when_no_tool_called(
    monkeypatch,
):
    agent = CustomerSupportAgent()

    response = SimpleNamespace(
        id="resp_3",
        output=[],
        output_text="I don't have enough information to answer that.",
    )

    create_mock = MagicMock(return_value=response)

    monkeypatch.setattr(
        agent.client.responses,
        "create",
        create_mock,
    )

    result = agent.handle(
        "Can you help me?",
        "cliente1988",
    )

    assert result == "I don't have enough information to answer that."
    assert create_mock.call_count == 1