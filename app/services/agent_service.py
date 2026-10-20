from collections.abc import AsyncIterator

from langchain_core.messages import AIMessageChunk

from app.agent.builder import build_agent
from app.agent.context import Context

class AgentService:
    def __init__(self):
        self.agent = build_agent()

    async def ask(self, question: str, user_id: str, session_id: str) -> str:
        config = {"configurable": {"thread_id": session_id}}
        context = Context(user_id=user_id, session_id=session_id)

        output = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            config = config,
            context = context,
        )
        return output["messages"][-1].content

    async def astream(self, question: str, user_id: str, session_id: str) -> AsyncIterator[str]:
        """流式输出：逐 token 产出模型的回答内容。"""
        config = {"configurable": {"thread_id": session_id}}
        context = Context(user_id=user_id, session_id=session_id)

        async for chunk, _meta in self.agent.astream(
            {"messages": [{"role": "user", "content": question}]},
            config = config,
            context = context,
            stream_mode = "messages",
        ):
            # 只取模型输出片段，过滤掉工具调用/工具结果等非回答内容
            if isinstance(chunk, AIMessageChunk) and isinstance(chunk.content, str) and chunk.content:
                yield chunk.content