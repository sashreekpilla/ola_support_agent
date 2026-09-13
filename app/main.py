from uuid import uuid4
import json, time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from app.models import AskRequest, AddDocumentRequest, SupportResponse
from app.pipeline import run, prepare
from app.memory import add_document
from app.governance import mask_pii, enforce_budget
from app.config import LOG_PATH, TOKEN_BUDGET

app=FastAPI(title="Ola Domain Support Agent")

@app.on_event("startup")
def startup(): prepare()


def log_request(trace_id, request_text, start, status="ok"):
    row={"trace_id":trace_id,"request":mask_pii(request_text),"duration_ms":round((time.perf_counter()-start)*1000,2),"status":status}
    with open(LOG_PATH,"a",encoding="utf-8") as f: f.write(json.dumps(row)+"\n")

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/ask", response_model=SupportResponse)
def ask(body:AskRequest):
    trace=uuid4().hex; start=time.perf_counter()
    try:
        enforce_budget(body.message,TOKEN_BUDGET)
        out=run(body.message,body.session_id); log_request(trace,body.message,start); return out
    except ValueError as e:
        log_request(trace,body.message,start,"rejected")
        raise HTTPException(status_code=413, detail=str(e))

@app.post("/add-document")
def add(body:AddDocumentRequest):
    return add_document(body.title,body.text)

@app.websocket("/chat")
async def chat(websocket:WebSocket):
    await websocket.accept()
    session_id=uuid4().hex
    try:
        while True:
            message=await websocket.receive_text()
            response=run(message,session_id)
            await websocket.send_json(response.model_dump())
    except WebSocketDisconnect:
        return
