import os, pickle
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from backend.rag.embeddings import get_embedding_model
from backend.core.logging import logger

VECTOR_DB_PATH = "./faiss_index.pkl"

def init_vector_store():
    try:
        logger.info("Initializing RAG FAISS Vector Store...")
        embeddings = get_embedding_model()
        docs_path = "backend/rag/documents/travel_tips.md"
        if not os.path.exists(VECTOR_DB_PATH):
            loader = TextLoader(docs_path)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            splits = splitter.split_documents(docs)
            db = FAISS.from_documents(splits, embeddings)
            with open(VECTOR_DB_PATH, "wb") as f: pickle.dump(db, f)
            logger.info("FAISS Vector DB created.")
        else:
            logger.info("FAISS Vector DB exists.")
    except Exception as e:
        logger.error(f"Failed to init FAISS: {e}")

def get_vector_retriever():
    try:
        embeddings = get_embedding_model()
        if os.path.exists(VECTOR_DB_PATH):
            with open(VECTOR_DB_PATH, "rb") as f: db = pickle.load(f)
            return db.as_retriever(search_kwargs={"k": 3})
        return None
    except Exception as e:
        logger.error(f"Failed to get retriever: {e}")
        return None