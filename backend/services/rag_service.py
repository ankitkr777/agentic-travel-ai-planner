from backend.rag.vector_store import get_vector_retriever
from backend.core.logging import logger

class RAGService:
    @staticmethod
    async def query_knowledge_base(query: str) -> str:
        try:
            retriever = get_vector_retriever()
            if not retriever: return "RAG unavailable."
            docs = await retriever.ainvoke(query)
            return "\n".join([d.page_content for d in docs])
        except Exception as e:
            logger.error(f"RAG Service Error: {e}")
            return "Error fetching knowledge."