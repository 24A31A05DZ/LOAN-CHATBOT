"""
Agentic AI Personal Loan Chatbot - Main Application
FastAPI backend with Master-Worker Agent architecture
"""

import os
import uuid
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from agents import master_agent

app = FastAPI(title="Personal Loan Chatbot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

sessions = {}


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    message: str
    show_upload: bool = False
    show_download: bool = False
    download_file: Optional[str] = None
    session_ended: bool = False


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the main chat interface"""
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main conversation endpoint
    Routes messages through Master Agent
    """
    print("\n" + "#"*60)
    print("# NEW CHAT REQUEST")
    print("#"*60)
    
    session_id = request.session_id
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = master_agent.get_initial_state()
        print(f"[MAIN] Created new session: {session_id}")
    
    session = sessions[session_id]
    print(f"[MAIN] Session ID: {session_id}")
    print(f"[MAIN] User message: {request.message}")
    
    response = master_agent.process_message(session, request.message)
    
    print(f"[MAIN] Agent response: {response.get('message', '')[:100]}...")
    print("#"*60 + "\n")
    
    return ChatResponse(
        session_id=session_id,
        message=response.get("message", ""),
        show_upload=response.get("show_upload", False),
        show_download=response.get("show_download", False),
        download_file=response.get("download_file"),
        session_ended=response.get("session_ended", False)
    )


@app.post("/upload-salary")
async def upload_salary(session_id: str, file: UploadFile = File(...)):
    """
    Salary slip upload endpoint
    Triggers salary verification in Underwriting Agent
    """
    print("\n" + "#"*60)
    print("# SALARY SLIP UPLOAD")
    print("#"*60)
    
    if session_id not in sessions:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    session = sessions[session_id]
    
    if file.content_type not in ["application/pdf", "image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload PDF or image.")
    
    filename = f"salary_{session_id}_{file.filename}"
    filepath = os.path.join("uploads", filename)
    
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    
    session["salary_slip_uploaded"] = True
    session["salary_slip_path"] = filepath
    print(f"[MAIN] Salary slip saved: {filename}")
    
    response = master_agent.process_salary_upload(session)
    
    print(f"[MAIN] Processing result: {response.get('message', '')[:100]}...")
    print("#"*60 + "\n")
    
    return JSONResponse({
        "success": True,
        "message": response.get("message", ""),
        "show_download": response.get("show_download", False),
        "download_file": response.get("download_file"),
        "session_ended": response.get("session_ended", False)
    })


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated sanction letter"""
    filepath = os.path.join("uploads", filename)
    if os.path.exists(filepath):
        return FileResponse(
            filepath,
            media_type="application/pdf",
            filename=filename
        )
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Agentic AI Personal Loan Chatbot is running"}


@app.post("/reset")
async def reset_session(session_id: str):
    """Reset a session"""
    if session_id in sessions:
        del sessions[session_id]
    return {"success": True, "message": "Session reset successfully"}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("Prototype ready: Agentic AI Personal Loan Chatbot running successfully")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=5000)
