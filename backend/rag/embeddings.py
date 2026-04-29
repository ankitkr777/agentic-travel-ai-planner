from langchain_huggingface import HuggingFaceEmbeddings
from backend.core.logging import logger

def get_embedding_model():
    try:
        # Runs 100% locally on your laptop. No API key needed.
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    except Exception as e:
        logger.error(f"Failed to load local HuggingFace embeddings: {e}")
        raise RuntimeError("Ensure 'sentence-transformers' is installed.")