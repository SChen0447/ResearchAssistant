from app.config import *
from app.llm import get_llm
from app.tools.rag_tool import knowledge_search
from app.tools.web_search import web_search
from app.agent.prompts import system_prompt
from app.agent.context import Context

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver


def build_agent():
    llm = get_llm()
    checkpointer = InMemorySaver()

    agent = create_agent(
        model = llm,
        system_prompt = system_prompt,
        tools = [knowledge_search, web_search],
        checkpointer = checkpointer,
        context_schema = Context,
    )
    return agent



if __name__ == "__main__":
    agent = build_agent()
    config = {"configurable": {"thread_id":"1"}}
    response = agent.invoke(
        {"messages":[{"role":"user", "content":"给我找几篇近几年的多目标优化的论文"}]},
        config=config,
        context=Context(user_id="1", session_id="1"),
    )
    print(response["messages"][-1].content)

