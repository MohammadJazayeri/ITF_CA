from __future__ import annotations

"""A minimal set of Synapse-style mediator classes.

This module intentionally keeps the footprint small—just enough to emulate
Apache Synapse’s Log / Filter / Send behaviour so that you can play with
a micro-ESB locally.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import aiohttp


class MessageContext:
    """Represents the in-flight message inside the ESB."""

    def __init__(self, method: str, path: str, headers: Dict[str, str], body: bytes):
        self.method = method
        self.path = path
        self.headers: Dict[str, str] = headers.copy()
        self.body: bytes = body
        # Arbitrary scratch-pad for mediators to share data
        self.properties: Dict[str, Any] = {}

        # The eventual HTTP response that will be returned to the original caller
        self.response_status: int = 200
        self.response_headers: Dict[str, str] = {}
        self.response_body: bytes = b""

    # Convenience helpers -------------------------------------------------
    def set_response(self, status: int, body: bytes, headers: Optional[Dict[str, str]] = None):
        self.response_status = status
        self.response_body = body
        if headers:
            self.response_headers = headers


class Mediator(ABC):
    """Base class all mediators derive from."""

    @abstractmethod
    async def mediate(self, ctx: MessageContext) -> None:  # pragma: no cover
        """Process the message *in-place*; may mutate ctx or perform side-effects."""
        raise NotImplementedError


class LogMediator(Mediator):
    """Logs something about the message."""

    def __init__(self, level: str = "INFO", message: Optional[str] = None):
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.message = message

    async def mediate(self, ctx: MessageContext) -> None:  # noqa: D401
        msg = self.message or f"{ctx.method} {ctx.path}"
        logging.log(self.level, msg)


class FilterMediator(Mediator):
    """Runs an expression; only continues if the result is truthy."""

    def __init__(self, expr: str, nested: Optional[List[Mediator]] = None):
        self.expr = expr
        self.nested = nested or []

    async def mediate(self, ctx: MessageContext) -> None:  # noqa: D401
        try:
            if eval(self.expr, {}, {"ctx": ctx}):  # nosec S307 – controlled input
                for m in self.nested:
                    await m.mediate(ctx)
        except Exception as exc:  # pragma: no cover
            logging.error("Filter expression '%s' raised %s", self.expr, exc, exc_info=True)


class SendMediator(Mediator):
    """Forward the (possibly mutated) message to an outbound endpoint."""

    def __init__(self, url: str):
        self.url = url

    async def mediate(self, ctx: MessageContext) -> None:  # noqa: D401
        async with aiohttp.ClientSession() as session:
            async with session.request(
                ctx.method,
                self.url,
                headers=ctx.headers,
                data=ctx.body,
            ) as resp:
                body = await resp.read()
                ctx.set_response(resp.status, body, dict(resp.headers))