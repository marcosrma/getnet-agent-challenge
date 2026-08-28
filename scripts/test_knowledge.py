from app.agents.knowledge import KnowledgeAgent


agent = KnowledgeAgent()

answer = agent.handle(
    "What's the difference between Get Classica and Get Smart?",
    "cliente1988",
)

print(answer)