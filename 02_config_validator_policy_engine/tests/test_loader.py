"""Tests for the loader module."""

import json
import pytest

from config_validator.loader import load_config


class TestLoadConfig:
    def test_load_yaml(self, tmp_path):
        f = tmp_path / "config.yaml"
        f.write_text("service:\n  name: test\n  image: test:1.0\n")
        data = load_config(f)
        assert data["service"]["name"] == "test"

    def test_load_json(self, tmp_path):
        f = tmp_path / "config.json"
        f.write_text(json.dumps({"service": {"name": "test", "image": "test:1.0"}}))
        data = load_config(f)
        assert data["service"]["name"] == "test"

    def test_invalid_yaml_raises(self, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text("just a plain string")
        # yaml.safe_load parses this as a string, which isn't a dict
        with pytest.raises(ValueError, match="must contain a mapping"):
            load_config(f)

    def test_non_dict_raises(self, tmp_path):
        f = tmp_path / "list.yaml"
        f.write_text("- item1\n- item2\n")
        with pytest.raises(ValueError, match="must contain a mapping"):
            load_config(f)
