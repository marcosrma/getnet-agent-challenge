from app.agents.router import AgentType, RouterAgent


router = RouterAgent()


def test_routes_product_question_to_knowledge():
    result = router.route(
        "What's the difference between the Get Classica and Get Smart?"
    )

    assert result == AgentType.KNOWLEDGE


def test_routes_customer_problem_to_support():
    result = router.route(
        "My card machine won't connect to the internet."
    )

    assert result == AgentType.CUSTOMER_SUPPORT


def test_routes_transaction_issue_to_support():
    result = router.route(
        "My transaction was declined."
    )

    assert result == AgentType.CUSTOMER_SUPPORT