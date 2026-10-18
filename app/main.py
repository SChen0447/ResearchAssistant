from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.agent_service import AgentService
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent_service = AgentService()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/research_assistant")

