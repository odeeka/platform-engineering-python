"""Thread-safe in-memory metrics collector."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass
class _Metrics:
    """Simple counters and latency tracking."""

    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    request_count: int = 0
    error_count: int = 0
    # path -> list of latencies in seconds
    latencies: dict[str, list[float]] = field(default_factory=dict)
    start_time: float = field(default_factory=time.monotonic)

    def record_request(self, path: str, latency: float, error: bool = False) -> None:
        with self._lock:
            self.request_count += 1
            if error:
                self.error_count += 1
            self.latencies.setdefault(path, []).append(latency)

    def snapshot(self) -> dict:
        """Return a JSON-serialisable snapshot of all metrics."""
        with self._lock:
            uptime = time.monotonic() - self.start_time
            per_path: dict[str, dict] = {}
            for path, lats in self.latencies.items():
                per_path[path] = {
                    "count": len(lats),
                    "avg_ms": round(sum(lats) / len(lats) * 1000, 2) if lats else 0,
                    "max_ms": round(max(lats) * 1000, 2) if lats else 0,
                }
            return {
                "uptime_s": round(uptime, 2),
                "request_count": self.request_count,
                "error_count": self.error_count,
                "paths": per_path,
            }

    def reset(self) -> None:
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self.request_count = 0
            self.error_count = 0
            self.latencies.clear()
            self.start_time = time.monotonic()


# Module-level singleton
metrics = _Metrics()
