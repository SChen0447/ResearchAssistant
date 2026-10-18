from app.config import *
from app.rag.loaders import load_pdf_data
from app.rag.splitters import split_documents
from app.rag.vectorstore import VectorStore
from app.rag.retriever import build_retriever
from app.rag.embeddings import BGEEmbeddings
from app.config import DATA_PATH, MILVUS_URI, EMBEDDING_MODEL

def main():
    documents = load_pdf_data(DATA_PATH)
    chunks = split_documents(documents)
    vectorstore = VectorStore(
        uri=MILVUS_URI, 
        collection_name="research_assistant", 
        embedding_model=EMBEDDING_MODEL,
    )
    vectorstore.build(chunks)

if __name__ == "__main__":
    main()