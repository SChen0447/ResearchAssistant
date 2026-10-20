import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
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

# 流式输出（SSE，逐 token 返回）
@router.post("/ask_stream")
async def ask_stream(req: AskRequest, request: Request) -> StreamingResponse:
    # 包装成sse事件格式 每条消息以 data: 开头，以 \n\n（两个换行）结尾
    def sse(payload: dict) -> str:
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    async def event_stream():
        try:
            async for token in request.app.state.agent_service.astream(
                question = req.question,
                user_id = req.user_id,
                session_id = req.session_id,
            ):
                yield sse({"delta": token})
        except Exception as exc:
            yield sse({"error": str(exc)})
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type = "text/event-stream", # 告诉浏览器这是sse流
        headers = {
            "Cache-Control": "no-cache", # 禁止浏览器缓存
            "X-Accel-Buffering": "no",   # 禁止反向代理缓冲，保证逐 token 下发
        },
    )