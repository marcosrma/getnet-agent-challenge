from app.rag.retriever import KnowledgeRetriever


retriever = KnowledgeRetriever()

results = retriever.retrieve(
    "What is the difference between Get Classica and Get Smart?"
)

for index, result in enumerate(results, start=1):
    print()
    print(f"RESULT {index}")
    print(f"Source: {result['source']}")
    print(f"Distance: {result['distance']:.4f}")
    print(result["text"][:600])