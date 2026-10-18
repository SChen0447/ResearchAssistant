import os
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# llm配置
LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY")
LLM_BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-flash"

# rag配置
DATA_PATH = "data/pumpkin_book.pdf"
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"

# Milvus向量库配置
MILVUS_URI = "http://localhost:19530"
COLLECTION_NAME = "research_assistant"

# tavily联网搜索
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Redis
REDIS_URL = "redis://localhost:6379"   #redis就用redis协议，不是http
REDIS_HOST = "localhost"
REDIS_PORT = "6379"




