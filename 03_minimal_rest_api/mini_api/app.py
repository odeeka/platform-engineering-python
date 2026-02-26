"""Flask application with /health, /metrics, /work endpoints."""

from __future__ import annotations

import time
import uuid
from functools import wraps

from flask import Flask, g, jsonify, request

from .logger import get_logger
from .metrics import metrics

log = get_logger()


def create_app(work_timeout: float = 5.0) -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config["WORK_TIMEOUT"] = work_timeout

    # ------------------------------------------------------------------
    # Middleware: request ID, timing, logging
    # ------------------------------------------------------------------
    @app.before_request
    def _before():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.start_time = time.monotonic()

    @app.after_request
    def _after(response):
        elapsed = time.monotonic() - g.start_time
        error = response.status_code >= 400
        metrics.record_request(request.path, elapsed, error=error)

        response.headers["X-Request-ID"] = g.request_id

        log.info(
            "%s %s -> %s",
            request.method,
            request.path,
            response.status_code,
            extra={
                "request_id": g.request_id,
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "elapsed_ms": round(elapsed * 1000, 2),
            },
        )
        return response

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------
    @app.get("/health")
    def health():
        """Liveness / readiness probe."""
        return jsonify({"status": "ok"})

    @app.get("/metrics")
    def metrics_endpoint():
        """Return collected metrics."""
        return jsonify(metrics.snapshot())

    @app.post("/work")
    def work():
        """Simulate work. Accepts JSON body:
        {
            "duration_s": 1.0   // simulated work duration (capped by timeout)
        }
        """
        body = request.get_json(silent=True) or {}
        duration = min(
            float(body.get("duration_s", 0.5)),
            app.config["WORK_TIMEOUT"],
        )
        if duration < 0:
            return jsonify({"error": "duration_s must be >= 0"}), 400

        time.sleep(duration)
        return jsonify({
            "result": "done",
            "worked_s": round(duration, 3),
            "request_id": g.request_id,
        })

    return app
