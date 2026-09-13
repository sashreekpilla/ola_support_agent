from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str = "default"

class AddDocumentRequest(BaseModel):
    title: str = Field(min_length=1)
    text: str = Field(min_length=20)

class SupportResponse(BaseModel):
    answer: str
    sources: list[str] = []
    ticket: dict | None = None
    session_id: str
    approved: bool = True

class VerdictModel(BaseModel):
    approved: bool
    final_answer: str
    reason: str
