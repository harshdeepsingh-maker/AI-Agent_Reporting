from __future__ import annotations
import os, asyncio
import httpx
from ..eventbus import EventBus, TOPIC_MARKETING_REQ, TOPIC_MARKETING_RES
from ..logging_utils import info, warn, error

class MarketingAgent:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.q = bus.subscribe(TOPIC_MARKETING_REQ)

    async def _fetch_http(self) -> dict:
        base = os.getenv("HTTP_BASE_URL", "http://127.0.0.1:8000")
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{base}/marketing")
            r.raise_for_status()
            return r.json()

    async def run(self):
        info("MarketingAgent_started")
        while True:
            _ = await self.q.get()  # any request payload
            try:
                data = await self._fetch_http()
                self.bus.publish(TOPIC_MARKETING_RES, {"status": "success", "data": data})
                info("MarketingAgent_ok")
            except Exception as e:
                error(f"MarketingAgent_failed: {e!r}")
                self.bus.publish(TOPIC_MARKETING_RES, {"status": "error", "error": str(e)})
