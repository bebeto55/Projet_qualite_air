"""Journalisation applicative (US-017 / US-018) et traçabilité sécurité."""
from __future__ import annotations

import logging
import threading
import time
from collections import deque
from logging.handlers import RotatingFileHandler

from settings import LOG_DIR

LOG_DIR.mkdir(parents=True, exist_ok=True)

_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


class MemoryHandler(logging.Handler):
    """Garde les N derniers logs en mémoire pour la page admin."""

    def __init__(self, capacity: int = 500):
        super().__init__()
        self.records: deque[dict] = deque(maxlen=capacity)

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        })


memory_handler = MemoryHandler()


def setup_logging() -> None:
    root = logging.getLogger()
    if getattr(root, "_smart_city_configured", False):
        return
    root.setLevel(logging.INFO)
    fmt = logging.Formatter(_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    file_handler = RotatingFileHandler(LOG_DIR / "api.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(fmt)
    memory_handler.setFormatter(fmt)

    for h in (console, file_handler, memory_handler):
        root.addHandler(h)
    root._smart_city_configured = True  # type: ignore[attr-defined]


security_log = logging.getLogger("security")
app_log = logging.getLogger("api")


class Metrics:
    """Métriques simples de performance (US-017)."""

    def __init__(self):
        self.started = time.time()
        self.requests = 0
        self.errors = 0
        self.total_ms = 0.0
        self.by_path: dict[str, dict] = {}
        self._lock = threading.Lock()

    def record(self, path: str, status: int, ms: float) -> None:
        with self._lock:
            self.requests += 1
            self.total_ms += ms
            if status >= 500:
                self.errors += 1
            p = self.by_path.setdefault(path, {"count": 0, "total_ms": 0.0, "max_ms": 0.0})
            p["count"] += 1
            p["total_ms"] += ms
            p["max_ms"] = max(p["max_ms"], ms)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "uptimeSeconds": int(time.time() - self.started),
                "requests": self.requests,
                "errors": self.errors,
                "avgResponseMs": round(self.total_ms / self.requests, 1) if self.requests else 0,
                "endpoints": {
                    k: {"count": v["count"], "avgMs": round(v["total_ms"] / v["count"], 1), "maxMs": round(v["max_ms"], 1)}
                    for k, v in sorted(self.by_path.items())
                },
            }


metrics = Metrics()
