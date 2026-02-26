"""Production server with graceful shutdown."""

from __future__ import annotations

import signal
import threading

from werkzeug.serving import make_server

from .app import create_app
from .logger import get_logger

log = get_logger()


def run_server(host: str = "0.0.0.0", port: int = 8080, work_timeout: float = 5.0) -> None:
    """Start the server and handle SIGTERM/SIGINT for graceful shutdown."""
    app = create_app(work_timeout=work_timeout)
    server = make_server(host, port, app, threaded=True)

    def _shutdown(signum, _frame):
        sig_name = signal.Signals(signum).name
        log.info("Received %s — shutting down gracefully", sig_name)
        # Shut down in a separate thread to avoid deadlock
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    log.info("Server starting on %s:%d (work_timeout=%.1fs)", host, port, work_timeout)
    server.serve_forever()
    log.info("Server stopped")
