from app.agent.builder import build_agent
from app.agent.context import Context

class AgentService:
    def __init__(self):
        self.agent = build_agent()

    def ask(self, question: str, user_id: str, session_id: str) -> str:
        config = {"configurable": {"thread_id": session_id}}
        context = Context(user_id=user_id, session_id=session_id)

        output = self.agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config = config,
            context = context,
        )
        return output["messages"][-1].content