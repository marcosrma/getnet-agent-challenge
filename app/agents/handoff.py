class HumanHandoffAgent:
    def handle(self, message: str, user_id: str) -> str:
        return (
            "Entendi que você precisa de atendimento humano. "
            "Esta conversa será encaminhada para um atendente, que poderá "
            "dar continuidade ao seu caso."
        )