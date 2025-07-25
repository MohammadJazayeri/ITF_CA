from __future__ import annotations

"""Demonstration script that talks to Service A, which in turn consults Service B.

Run both servers in separate shells:

    # Terminal 1
    uvicorn mcp_services.service_b:app --port 9002 --reload

    # Terminal 2
    SERVICE_B_URL=http://localhost:9002/mcp uvicorn mcp_services.service_a:app --port 9001 --reload

Then execute this script:

    python -m mcp_services.demo_connect
"""

import asyncio
import json

import httpx


async def main() -> None:  # noqa: D401
    question = "How are you, Service B?"
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://localhost:9001/mcp", json={"question": question})
        resp.raise_for_status()
        conversation = resp.json()["conversation"]

    print("Conversation:")
    for turn in conversation:
        role = turn["role"].capitalize()
        content = turn["content"]
        print(f"{role}: {content}")


if __name__ == "__main__":
    asyncio.run(main())