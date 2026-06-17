import asyncio
import os
from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
import sys

from docs_tool import append_to_doc
from gmail_tool import create_email_draft

app = FastAPI(title="Google MCP Server")

API_KEY = os.environ.get("API_KEY") or os.environ.get("MCP_API_KEY") or os.environ.get("api_key")

class DocRequest(BaseModel):
    doc_id: str
    content: str

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str

async def check_approval(action_name: str, payload: dict, x_api_key: str = None) -> bool:
    """
    If API_KEY is set in the environment, verifies the header.
    Otherwise, falls back to the interactive terminal prompt.
    """
    if API_KEY:
        if x_api_key != API_KEY:
            print(f"Rejected {action_name}: Invalid API Key.")
            return False
        return True

    print(f"\n--- ACTION REQUIRED ---")
    print(f"Action: {action_name}")
    print(f"Payload: {payload}")
    
    # Run the blocking input() inside a thread pool to avoid blocking the event loop
    response = await asyncio.to_thread(input, "Approve? (y/n): ")
    return response.strip().lower() == 'y'

@app.post("/append_to_doc")
async def append_doc_endpoint(request: DocRequest, x_api_key: str = Header(None)):
    payload = request.model_dump()
    approved = await check_approval("append_to_doc", payload, x_api_key)
    
    if not approved:
        raise HTTPException(status_code=403, detail="Action rejected (Interactive decline or Invalid API Key).")
        
    result = await asyncio.to_thread(append_to_doc, request.doc_id, request.content)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    return result

@app.post("/create_email_draft")
async def email_draft_endpoint(request: EmailRequest, x_api_key: str = Header(None)):
    payload = request.model_dump()
    approved = await check_approval("create_email_draft", payload, x_api_key)
    
    if not approved:
        raise HTTPException(status_code=403, detail="Action rejected (Interactive decline or Invalid API Key).")
        
    result = await asyncio.to_thread(create_email_draft, request.to_email, request.subject, request.body)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    return result
