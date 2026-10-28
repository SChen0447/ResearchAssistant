from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.services.agent_service import AgentService
from app.api.routes import router

from prometheus_fastapi_instrumentator import Instrumentator

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

# 指标采集中间件；expose 必须在 mount 之前，否则 /metrics 会被静态挂载吃掉
Instrumentator(
    should_group_status_codes = False,        # 保留精确状态码，便于区分 4xx / 5xx
    should_exclude_streaming_duration = True, # SSE 流式时长不计入 HTTP 延迟，避免 P95 被拖偏
    should_instrument_requests_inprogress = True,
    inprogress_labels = True,
    excluded_handlers = [r"/research_assistant/metrics"],  # 不统计抓取端点自身
).instrument(app).expose(
    app,
    endpoint = "/research_assistant/metrics",
    include_in_schema = False,
)


app.include_router(router, prefix="/research_assistant")

# 挂在最后：具体 API 路由先匹配，根挂载仅兜底静态资源
app.mount("/research_assistant", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

