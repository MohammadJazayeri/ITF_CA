from __future__ import annotations

"""Service B — an MCP server that answers questions.

It exposes a single POST /mcp endpoint that accepts a JSON body like:
    {"question": "..."}
And replies with:
    {"answer": "..."}

This keeps the protocol extremely small, but demonstrates two MCP services
interacting over HTTP.
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MCP Service B", version="1.0.0")


class Question(BaseModel):
    question: str


@app.post("/mcp")
async def answer(payload: Question):  # noqa: D401
    q = payload.question.strip()
    # ───────────────────────────────────────────────────────────────────
    # This is where you would call an LLM or other complex logic.
    # For demo purposes, we return a canned response.
    # ───────────────────────────────────────────────────────────────────
    reply = f"Service B here; thanks for asking: ‘{q}’. I’m great!"
    return {"answer": reply}