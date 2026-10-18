from pydantic import BaseModel


class AskRequest(BaseModel):
    user_id: str
    session_id: str
    question: str

class AskResponse(BaseModel):
    user_id: str
    session_id: str
    question: str
    answer: str