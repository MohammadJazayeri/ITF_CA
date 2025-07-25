from __future__ import annotations

"""Entrypoint: runs a very small HTTP ESB using the mediation engine."""

import asyncio
import logging
import os
from pathlib import Path

from aiohttp import web

from simple_synapse.config_loader import ConfigLoader
from simple_synapse.mediators import MessageContext

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

# ---------------------------------------------------------------------------
# Configuration loading
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True)
loader = ConfigLoader(CONFIG_DIR)
loader.refresh()
DEFAULT_SEQUENCE = os.getenv("SEQUENCE", "main")


# ---------------------------------------------------------------------------
# HTTP handlers
# ---------------------------------------------------------------------------
async def handle(request: web.Request) -> web.StreamResponse:  # noqa: D401
    body = await request.read()
    ctx = MessageContext(request.method, request.path_qs, dict(request.headers), body)

    # Run through the mediation pipeline ---------------------------------
    loader.refresh()  # hot-reload configs on every request (small toy server)
    await loader.get(DEFAULT_SEQUENCE).process(ctx)

    # Build the outgoing response ----------------------------------------
    return web.Response(status=ctx.response_status, headers=ctx.response_headers, body=ctx.response_body)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> web.Application:  # noqa: D401
    app = web.Application()
    # Catch-all route (acts like a typical Synapse proxy)
    app.router.add_route("*", "{tail:.*}", handle)
    return app


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    web.run_app(create_app(), port=port)