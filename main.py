
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import os
import httpx
import re

app = FastAPI(title="Agent Seatbelt - AI Agent Firewall", version="1.0.0")

# === FIREWALL RULES ===
BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard previous",
    "ignore your instructions",
    "delete all",
    "drop all tables",
    "send all data",
    "exfiltrate data",
    "reveal system prompt",
    "show system instructions",
    "bypass safety",
    "dan mode",
    "jailbreak"
]

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "gpt-4o"
    messages: List[Message]
    temperature: Optional[float] = 0.7

@app.get("/")
def health():
    return {
        "status": "Agent Seatbelt is running - We Got Your Back",
        "firewall": "active",
        "blocked_patterns": len(BLOCKED_PATTERNS),
        "docs": "/docs"
    }

@app.post("/v1/chat/completions")
async def firewall_proxy(req: ChatRequest):
    full_text = " ".join([m.content for m in req.messages]).lower()
    
    # Check for attacks
    for pattern in BLOCKED_PATTERNS:
        if pattern in full_text:
            return {
                "blocked": True,
                "reason": f"Blocked by Agent Seatbelt: Potential prompt injection detected",
                "attack_detected": pattern,
                "message": "We have your back - this attack was stopped before reaching your AI agent.",
                "status": "protected"
            }
    
    # If clean, forward to OpenAI (if key exists) or return mock success
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "blocked": False,
            "status": "clean - would forward to OpenAI (set OPENAI_API_KEY env var to enable forwarding)",
            "model": req.model,
            "message": "Your agent is protected. Add your OpenAI key in Render to enable full proxy."
        }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=req.model_dump(),
                timeout=30.0
            )
            return resp.json()
    except Exception as e:
        return {"error": str(e), "note": "Firewall is active, but forwarding failed"}
