from app.config import *
from langchain.tools import tool
from app.rag.vectorstore import VectorStore
from app.rag.retriever import build_retriever


_vectorstore = None
_retriever = None

def get_retriever():
    """懒加载"""
    global _vectorstore, _retriever
    if _retriever is None:
        _vectorstore = VectorStore(uri=MILVUS_URI, collection_name=COLLECTION_NAME, embedding_model=EMBEDDING_MODEL)
        _vectorstore.load()
        _retriever = build_retriever(_vectorstore)
    return _retriever


@tool
def knowledge_search(query: str) -> str:
    """
    搜索机器学习知识库，当用户问题涉及到本地知识库相关内容时使用

    Args:
        query: 搜索查询。必须完整、独立，不含指代词。
    Returns:
        相关文档片段
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)

    results = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        results.append(f"[{i}]来源：{source}\n{doc.page_content}")

    return "\n\n".join(results)


