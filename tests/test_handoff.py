from app.agents.handoff import HumanHandoffAgent


def test_handoff_agent_is_transparent_about_escalation():
    response = HumanHandoffAgent().handle(
        "I want to speak with a human agent",
        "cliente1988",
    )

    assert "encaminhada para um atendente" in response
    assert "ticket" not in response.lower()