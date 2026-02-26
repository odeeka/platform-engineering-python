"""Unit tests for the metrics collector."""

import time

from mini_api.metrics import _Metrics


class TestMetrics:
    def setup_method(self):
        self.m = _Metrics()

    def test_record_request(self):
        self.m.record_request("/health", 0.01)
        assert self.m.request_count == 1
        assert self.m.error_count == 0

    def test_record_error(self):
        self.m.record_request("/work", 0.05, error=True)
        assert self.m.error_count == 1

    def test_snapshot(self):
        self.m.record_request("/health", 0.01)
        self.m.record_request("/health", 0.03)
        snap = self.m.snapshot()
        assert snap["request_count"] == 2
        assert "/health" in snap["paths"]
        assert snap["paths"]["/health"]["count"] == 2
        assert snap["paths"]["/health"]["avg_ms"] > 0

    def test_reset(self):
        self.m.record_request("/x", 0.1)
        self.m.reset()
        snap = self.m.snapshot()
        assert snap["request_count"] == 0
        assert snap["paths"] == {}

    def test_uptime(self):
        time.sleep(0.05)
        snap = self.m.snapshot()
        assert snap["uptime_s"] >= 0.04
