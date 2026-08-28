from app.tools.customer import (
    get_customer_profile,
    get_settlement_schedule,
    get_terminal_status,
)


def test_get_customer_profile():
    result = get_customer_profile("cliente1988")

    assert result["found"] is True
    assert result["name"] == "João Silva"
    assert result["segment"] == "SMB"


def test_get_settlement_schedule():
    result = get_settlement_schedule("cliente1988")

    assert result["found"] is True
    assert result["expected_deposit_date"] == "2026-08-28"
    assert result["status"] == "scheduled"


def test_get_terminal_status():
    result = get_terminal_status("cliente2001")

    assert result["found"] is True
    assert result["id"] == "POS-99881"
    assert result["status"] == "offline"


def test_customer_not_found():
    result = get_customer_profile("unknown-user")

    assert result["found"] is False