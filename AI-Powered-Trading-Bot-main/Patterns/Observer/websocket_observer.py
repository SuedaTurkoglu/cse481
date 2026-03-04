import asyncio
import datetime
from typing import Any, Dict, Optional

from .observer import Observer


class WebSocketObserver(Observer):
    """Observer that streams bot messages over a WebSocket session."""

    def __init__(
        self,
        session_id: str,
        queue: Optional["asyncio.Queue[Dict[str, Any]]"] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        fallback_to_console: bool = True,
    ):
        self.session_id = session_id
        self._queue = queue
        self._loop = loop
        self._fallback = fallback_to_console or queue is None or loop is None
        self.messages: list[Dict[str, Any]] = []

    def _send_payload(self, payload: Dict[str, Any]):
        """Schedule payload delivery on the FastAPI event loop."""
        if self._queue and self._loop and not self._fallback:
            asyncio.run_coroutine_threadsafe(self._queue.put(payload), self._loop)
        else:
            self.messages.append(payload)

    def update(self, message: str):
        payload = {
            "type": "log",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
            "session_id": self.session_id,
        }
        self._send_payload(payload)

    def send_result(self, final_balance: float, initial_balance: float):
        profit_loss = final_balance - initial_balance
        profit_pct = (profit_loss / initial_balance * 100) if initial_balance else 0.0
        payload = {
            "type": "result",
            "final_balance": final_balance,
            "profit_loss": profit_loss,
            "profit_pct": profit_pct,
            "session_id": self.session_id,
        }
        self._send_payload(payload)

    def send_error(self, error_message: str):
        payload = {
            "type": "error",
            "message": error_message,
            "session_id": self.session_id,
        }
        self._send_payload(payload)
