from app.rag.vectorstore import VectorStore

def build_retriever(vectorstore: VectorStore):
    return vectorstore.as_retriever()
