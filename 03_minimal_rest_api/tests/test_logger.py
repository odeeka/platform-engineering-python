"""Tests for the JSON logger."""

import json
import logging

from mini_api.logger import JSONFormatter


class TestJSONFormatter:
    def test_formats_as_json(self):
        fmt = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="hello %s", args=("world",), exc_info=None,
        )
        line = fmt.format(record)
        data = json.loads(line)
        assert data["message"] == "hello world"
        assert data["level"] == "INFO"
        assert "timestamp" in data

    def test_includes_extra_fields(self):
        fmt = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="req", args=(), exc_info=None,
        )
        record.request_id = "abc-123"
        record.method = "GET"
        line = fmt.format(record)
        data = json.loads(line)
        assert data["request_id"] == "abc-123"
        assert data["method"] == "GET"
