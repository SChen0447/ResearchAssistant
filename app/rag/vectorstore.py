from app.rag.embeddings import BGEEmbeddings
from langchain_milvus import Milvus


class VectorStore:
    def __init__(self, uri: str, collection_name: str, embedding_model: str):
        self.uri = uri
        self.collection_name = collection_name
        self.embeddings = BGEEmbeddings(model_name=embedding_model)
        self._vectorstore : Milvus|None = None
        self._connection_args = {"uri": uri}
    
    def build(self, chunks, force_rebuild: bool = False):
        """构建或重建向量数据库"""
        from pymilvus import connections, utility
        connections.connect(uri=self.uri)
        is_exist = utility.has_collection(self.collection_name)

        if is_exist and not force_rebuild:
            raise ValueError(f"Collection {self.collection_name} already exists. Please set force_rebuild=True to rebuild it.")
            
        if force_rebuild:
            if is_exist:
                utility.drop_collection(self.collection_name)

        print(f"正在构建向量数据库 {self.collection_name}")
        self._vectorstore = Milvus.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            connection_args=self._connection_args,
            index_params={
                "index_type": "HNSW",
                "metric_type": "COSINE",
                "params": {"M": 16, "efConstruction": 200}
            },
            search_params={
                "metric_type": "COSINE",
                "params": {"ef": 64}
            },
            drop_old = False
        )
        print(f"向量数据库 {self.collection_name} 构建完成")


    def load(self):
        """加载向量数据库"""
        print(f"正在加载向量数据库 {self.collection_name}")
        self._vectorstore = Milvus(
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
            connection_args=self._connection_args,
            search_params={
                "metric_type": "COSINE",
                "params": {"ef": 64}
            },
        )
        print(f"向量数据库 {self.collection_name} 加载完成")
    

    def search(self, query: str, k: int = 5):
        """搜索向量数据库"""
        if self._vectorstore is None:
            raise ValueError("向量数据库未加载，请先调用 load() 方法加载数据库。")
        return self._vectorstore.similarity_search(query, k=k)
    
    def as_retriever(self):
        """将向量数据库封装为检索器"""
        if self._vectorstore is None:
            raise ValueError("向量数据库未加载，请先调用 load() 方法加载数据库。")
        return self._vectorstore.as_retriever() # 返回一个Embedding检索器对象


        