from fastapi import APIRouter, Request
from app.api.schemas import AskRequest, AskResponse

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/ask")
async def ask(req: AskRequest, request: Request) -> AskResponse:
    answer = await request.app.state.agent_service.ask(
        question = req.question,
        user_id = req.user_id,
        session_id = req.session_id,
    )
    return AskResponse(
        question = req.question,
        user_id = req.user_id,
        session_id = req.session_id,
        answer = answer
    )

