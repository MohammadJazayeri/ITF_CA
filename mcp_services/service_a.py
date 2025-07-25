from __future__ import annotations

"""Service A — an MCP server that delegates to Service B.

POST /mcp takes a JSON body {"question": "..."} and returns a conversation
containing both users’ input and Service B’s response.

Service B’s URL can be configured via the SERVICE_B_URL env var.
"""

import os

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://localhost:9002/mcp")

app = FastAPI(title="MCP Service A", version="1.0.0")


class Question(BaseModel):
    question: str


@app.post("/mcp")
async def converse(payload: Question):  # noqa: D401
    question = payload.question.strip()
    # Call Service B
    async with httpx.AsyncClient() as client:
        resp = await client.post(SERVICE_B_URL, json={"question": question})
        resp.raise_for_status()
        answer = resp.json()["answer"]
    # Aggregate conversation
    return {
        "conversation": [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    }