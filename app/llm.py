from functools import lru_cache
from langchain_openai import ChatOpenAI
from langchain_redis import RedisCache
from langchain_litellm import ChatLiteLLM
from langchain_core.globals import set_llm_cache
import litellm
from litellm.caching import Cache
from app.config import *


# set_llm_cache(RedisCache(redis_url=REDIS_URL, ttl=600))  # 不能直接套用给liteLLM

# @lru_cache(maxsize=1) # 把函数的返回值按参数缓存起来，相同参数再次调用时直接返回缓存结果，不再执行函数体
# def get_llm():
#     return ChatOpenAI(
#         api_key=LLM_API_KEY,   
#         base_url=LLM_BASE_URL,
#         model_name=LLM_MODEL,
#         temperature=0,
#     )

# # LiteLLM 自带的缓存：能正确序列化 LiteLLM 的响应，且天然支持后续切换多模型
litellm.cache = Cache(type="redis", host=REDIS_HOST, port=REDIS_PORT, ttl=600)

@lru_cache(maxsize=1) # 把函数的返回值按参数缓存起来，相同参数再次调用时直接返回缓存结果，不再执行函数体
def get_llm() -> ChatLiteLLM:
    return ChatLiteLLM(
        api_key=LLM_API_KEY,   
        api_base=LLM_BASE_URL,
        model=f"deepseek/{LLM_MODEL}",
        temperature=0,
    )

if __name__ == "__main__":
    llm = get_llm()
    print(llm.invoke("我如果说我爱你你会怎么回答我？"))
    print(llm.invoke("我如果说我爱你你会怎么回答我？"))
    