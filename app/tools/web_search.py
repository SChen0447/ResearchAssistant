from app.config import *
from langchain.tools import tool
from langchain_tavily import TavilySearch

_tavily = None

def get_tavily():
    global _tavily
    if _tavily is None:
        _tavily = TavilySearch(api_key=TAVILY_API_KEY, max_results=5)
    return _tavily

@tool
async def web_search(query: str) -> str:
    """
    联网搜索，返回相关结果

    Args:
        query: 搜索查询。必须完整、独立，不含指代词。
    Returns:
        相关网页片段
    """
    tavily = get_tavily()
    results = await tavily.ainvoke({"query": query})
    if not results:
        return "没有找到相关结果"
    
    items = results.get("results", [])
    answer = results.get("answer")
    
    output=[]
    if answer:
        output.append(f"AI摘要: {answer}\n")
        
    for i, r in enumerate(items, 1):
        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "")
        output.append(f"[{i}] {title}\nURL：{url}\n{content}")

    return "\n\n".join(output)
    