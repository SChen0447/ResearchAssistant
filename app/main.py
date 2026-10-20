from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.services.agent_service import AgentService
from app.api.routes import router

# 把懒加载改成预热
from app.tools.rag_tool import get_retriever
import asyncio

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent_service = AgentService()
    await asyncio.to_thread(get_retriever)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/research_assistant")

# 挂在最后：具体 API 路由先匹配，根挂载仅兜底静态资源
app.mount("/research_assistant", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

