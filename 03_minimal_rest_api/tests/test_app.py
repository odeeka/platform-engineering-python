"""Unit and integration tests for the Flask app."""

from __future__ import annotations

import json

import pytest

from mini_api.app import create_app
from mini_api.metrics import metrics


@pytest.fixture()
def client():
    app = create_app(work_timeout=2.0)
    app.config["TESTING"] = True
    metrics.reset()
    with app.test_client() as c:
        yield c


class TestHealth:
    def test_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ok"

    def test_request_id_header(self, client):
        resp = client.get("/health")
        assert "X-Request-ID" in resp.headers


class TestMetricsEndpoint:
    def test_returns_200(self, client):
        client.get("/health")
        resp = client.get("/metrics")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "request_count" in data
        assert data["request_count"] >= 1

    def test_tracks_paths(self, client):
        client.get("/health")
        client.get("/health")
        resp = client.get("/metrics")
        data = resp.get_json()
        assert "/health" in data["paths"]
        assert data["paths"]["/health"]["count"] == 2


class TestWork:
    def test_default_work(self, client):
        resp = client.post("/work", json={})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["result"] == "done"
        assert "request_id" in data

    def test_custom_duration(self, client):
        resp = client.post("/work", json={"duration_s": 0.1})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["worked_s"] <= 0.2  # some tolerance

    def test_timeout_caps_duration(self, client):
        # work_timeout is 2.0, so 10.0 should be capped
        resp = client.post("/work", json={"duration_s": 10.0})
        data = resp.get_json()
        assert data["worked_s"] <= 2.1

    def test_negative_duration(self, client):
        resp = client.post("/work", json={"duration_s": -1})
        assert resp.status_code == 400

    def test_no_body(self, client):
        resp = client.post("/work")
        assert resp.status_code == 200


class TestRequestID:
    def test_propagates_provided_id(self, client):
        resp = client.get("/health", headers={"X-Request-ID": "my-id-123"})
        assert resp.headers["X-Request-ID"] == "my-id-123"

    def test_generates_id_when_missing(self, client):
        resp = client.get("/health")
        rid = resp.headers["X-Request-ID"]
        assert len(rid) > 0


class TestNotFound:
    def test_404(self, client):
        resp = client.get("/nonexistent")
        assert resp.status_code == 404
