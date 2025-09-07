from __future__ import annotations
import asyncio
from collections import defaultdict
from typing import Any, Dict, List, DefaultDict

# ==== Topic names expected by agents ====
TOPIC_SALES_REQ      = "sales_request"
TOPIC_SALES_RES      = "sales_result"
TOPIC_MARKETING_REQ  = "marketing_request"
TOPIC_MARKETING_RES  = "marketing_result"

# Back-compat short aliases (some code imports these)
TOPIC_MKT_REQ = TOPIC_MARKETING_REQ
TOPIC_MKT_RES = TOPIC_MARKETING_RES

class EventBus:
    """
    Tiny in-memory event bus for async agents.

    Supports:
      - publish(topic, payload): broadcast to subscribers + complete any pending requests
      - request(topic, timeout): await next value (or last cached)
      - subscribe(topic): get an asyncio.Queue that receives every publish for that topic
      - unsubscribe(topic, queue): stop receiving
    """
    def __init__(self) -> None:
        self._last: Dict[str, Any] = {}                              # last payload per topic
        self._waiters: DefaultDict[str, List[asyncio.Future]] = defaultdict(list)
        self._subs: DefaultDict[str, List[asyncio.Queue]] = defaultdict(list)
        self._lock = asyncio.Lock()

    # --- pub/sub ---
    def subscribe(self, topic: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subs[topic].append(q)
        return q

    def unsubscribe(self, topic: str, q: asyncio.Queue) -> None:
        if q in self._subs.get(topic, []):
            self._subs[topic].remove(q)

    def publish(self, topic: str, payload: Any) -> None:
        # cache last
        self._last[topic] = payload
        # satisfy any pending "request" waiters
        waiters = self._waiters.get(topic, [])
        for fut in list(waiters):
            if not fut.done():
                fut.set_result(payload)
        self._waiters[topic].clear()
        # fan-out to subscribers
        for q in list(self._subs.get(topic, [])):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                # if a consumer is too slow, drop (or you could use put with a timeout)
                pass

    # alias for fire-and-forget
    def emit(self, topic: str, payload: Any) -> None:
        self.publish(topic, payload)

    # --- request/response ---
    async def request(self, topic: str, timeout: float | None = None) -> Any:
        async with self._lock:
            if topic in self._last:
                return self._last[topic]
            fut: asyncio.Future = asyncio.get_running_loop().create_future()
            self._waiters[topic].append(fut)

        try:
            if timeout is not None:
                return await asyncio.wait_for(fut, timeout=timeout)
            return await fut
        finally:
            # clean up waiter if still present
            async with self._lock:
                if fut in self._waiters.get(topic, []):
                    self._waiters[topic].remove(fut)
