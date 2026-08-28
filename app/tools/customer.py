import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "customers.json"


def _load_customers() -> dict:
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_customer_profile(user_id: str) -> dict:
    customers = _load_customers()
    customer = customers.get(user_id)

    if not customer:
        return {
            "found": False,
            "user_id": user_id,
        }

    return {
        "found": True,
        "user_id": user_id,
        "name": customer["name"],
        "segment": customer["segment"],
    }


def get_settlement_schedule(user_id: str) -> dict:
    customers = _load_customers()
    customer = customers.get(user_id)

    if not customer:
        return {
            "found": False,
            "user_id": user_id,
        }

    return {
        "found": True,
        "user_id": user_id,
        **customer["settlement"],
    }


def get_terminal_status(user_id: str) -> dict:
    customers = _load_customers()
    customer = customers.get(user_id)

    if not customer:
        return {
            "found": False,
            "user_id": user_id,
        }

    return {
        "found": True,
        "user_id": user_id,
        **customer["terminal"],
    }