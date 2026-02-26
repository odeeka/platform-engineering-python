"""Tests for schema validation."""

from config_validator.schema import validate_schema


VALID_CONFIG = {
    "service": {
        "name": "my-api",
        "image": "registry/my-api:1.0.0",
        "replicas": 3,
        "port": 8080,
        "health_check": "/healthz",
    }
}


class TestRequiredFields:
    def test_valid_config_no_issues(self):
        issues = validate_schema(VALID_CONFIG)
        errors = [i for i in issues if i.severity.value == "error"]
        assert errors == []

    def test_missing_name(self):
        data = {"service": {"image": "x:1.0"}}
        issues = validate_schema(data)
        paths = [i.path for i in issues if i.rule == "required_field"]
        assert "service.name" in paths

    def test_missing_image(self):
        data = {"service": {"name": "x"}}
        issues = validate_schema(data)
        paths = [i.path for i in issues if i.rule == "required_field"]
        assert "service.image" in paths

    def test_empty_config(self):
        issues = validate_schema({})
        errors = [i for i in issues if i.rule == "required_field"]
        assert len(errors) >= 2  # at least name + image


class TestTypeChecks:
    def test_wrong_type_replicas(self):
        data = {"service": {"name": "x", "image": "x:1.0", "replicas": "three"}}
        issues = validate_schema(data)
        type_issues = [i for i in issues if i.rule == "type_check"]
        assert len(type_issues) == 1
        assert type_issues[0].path == "service.replicas"

    def test_wrong_type_port(self):
        data = {"service": {"name": "x", "image": "x:1.0", "port": "http"}}
        issues = validate_schema(data)
        type_issues = [i for i in issues if i.rule == "type_check"]
        assert any(i.path == "service.port" for i in type_issues)


class TestEnvironmentRules:
    def test_prod_requires_replicas(self):
        data = {"service": {"name": "x", "image": "x:1.0"}}
        issues = validate_schema(data, environment="prod")
        env_issues = [i for i in issues if i.rule == "env_required"]
        paths = [i.path for i in env_issues]
        assert "service.replicas" in paths
        assert "service.health_check" in paths

    def test_stage_requires_replicas(self):
        data = {"service": {"name": "x", "image": "x:1.0"}}
        issues = validate_schema(data, environment="stage")
        paths = [i.path for i in issues if i.rule == "env_required"]
        assert "service.replicas" in paths

    def test_dev_no_extra_requirements(self):
        data = {"service": {"name": "x", "image": "x:1.0"}}
        issues = validate_schema(data, environment="dev")
        env_issues = [i for i in issues if i.rule == "env_required"]
        assert env_issues == []
