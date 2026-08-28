import chromadb
from openai import OpenAI

from app.config import settings


class KnowledgeRetriever:
    def __init__(self):
        self.openai_client = OpenAI(
            api_key=settings.openai_api_key
        )

        self.chroma_client = chromadb.PersistentClient(
            path=settings.vector_db_path
        )

        self.collection = self.chroma_client.get_collection(
            name="getnet_knowledge"
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        embedding_response = self.openai_client.embeddings.create(
            model=settings.embedding_model,
            input=query,
        )

        query_embedding = embedding_response.data[0].embedding

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        return [
            {
                "text": document,
                "source": metadata["source"],
                "title": metadata["title"],
                "distance": distance,
            }
            for document, metadata, distance in zip(
                documents,
                metadatas,
                distances,
            )
        ]