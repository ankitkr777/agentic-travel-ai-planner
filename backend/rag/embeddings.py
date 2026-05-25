from langchain.embeddings.fake import FakeEmbeddings

def get_embedding_model():
    return FakeEmbeddings(size=384)