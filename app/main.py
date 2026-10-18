from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.agent_service import AgentService
from app.api.routes import router

# 把懒加载改成预热
from app.tools.rag_tool import get_retriever
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent_service = AgentService()
    await asyncio.to_thread(get_retriever)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/research_assistant")

