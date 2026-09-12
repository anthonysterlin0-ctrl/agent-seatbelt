from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI(title="Agent Seatbelt - OpenRouter Edition")

BLOCKED = ["ignore previous instructions", "ignore all previous", "delete all", "send all data", "reveal system prompt", "drop all tables", "bypass safety", "dan mode", "jailbreak", "exfiltrate"]

@app.get("/")
def health():
    return {"status": "live", "firewall": "OpenRouter + OpenAI compatible", "we_got_your_back": True, "docs": "/docs"}

@app.post("/v1/chat/completions")
async def firewall(request: Request):
    body = await request.json()
    text = " ".join([m.get("content","") for m in body.get("messages",[])]).lower()
    
    for b in BLOCKED:
        if b in text:
            return JSONResponse(content={
                "blocked": True,
                "reason": f"Blocked by Agent Seatbelt: {b}",
                "attack": b,
                "we_got_your_back": "Stopped before reaching your model"
            })

    # Get customer's key from their request
    auth = request.headers.get("authorization")
    if not auth:
        return JSONResponse(content={"error": "Add Authorization: Bearer sk-or-v1-... or sk-proj-..."}, status_code=401)

    # Auto-detect if it's OpenRouter or OpenAI key
    is_openrouter = "sk-or-" in auth
    forward_url = "https://openrouter.ai/api/v1/chat/completions" if is_openrouter else "https://api.openai.com/v1/chat/completions"
    
    # Forward using customer's key - you pay $0
    headers = {"Authorization": auth, "Content-Type": "application/json"}
    if is_openrouter:
        headers["HTTP-Referer"] = "https://agent-seatbelt.com"
        headers["X-Title"] = "Agent Seatbelt"

    async with httpx.AsyncClient() as client:
        r = await client.post(forward_url, headers=headers, json=body, timeout=60)
        return JSONResponse(content=r.json(), status_code=r.status_code)
