"""Tests for policy engine."""

from config_validator.policies import (
    evaluate_policies,
    health_check_warning,
    minimum_replicas,
    no_latest_image,
    port_range,
)


class TestNoLatestImage:
    def test_explicit_latest(self):
        data = {"service": {"image": "myapp:latest"}}
        issues = no_latest_image(data)
        assert len(issues) == 1
        assert issues[0].rule == "no_latest_image"

    def test_implicit_latest_no_tag(self):
        data = {"service": {"image": "myapp"}}
        issues = no_latest_image(data)
        assert len(issues) == 1

    def test_pinned_tag(self):
        data = {"service": {"image": "myapp:1.2.3"}}
        assert no_latest_image(data) == []

    def test_missing_image_no_error(self):
        assert no_latest_image({}) == []


class TestMinimumReplicas:
    def test_below_minimum(self):
        data = {"service": {"replicas": 1}}
        issues = minimum_replicas(data)
        assert len(issues) == 1

    def test_at_minimum(self):
        data = {"service": {"replicas": 2}}
        assert minimum_replicas(data) == []

    def test_above_minimum(self):
        data = {"service": {"replicas": 5}}
        assert minimum_replicas(data) == []

    def test_missing_replicas_no_error(self):
        assert minimum_replicas({}) == []

    def test_custom_minimum(self):
        data = {"service": {"replicas": 3}}
        issues = minimum_replicas(data, minimum=5)
        assert len(issues) == 1


class TestPortRange:
    def test_valid_port(self):
        data = {"service": {"port": 8080}}
        assert port_range(data) == []

    def test_zero_port(self):
        data = {"service": {"port": 0}}
        assert len(port_range(data)) == 1

    def test_too_high(self):
        data = {"service": {"port": 70000}}
        assert len(port_range(data)) == 1


class TestHealthCheckWarning:
    def test_missing_warns(self):
        issues = health_check_warning({"service": {}})
        assert len(issues) == 1
        assert issues[0].severity.value == "warning"

    def test_present_ok(self):
        data = {"service": {"health_check": "/health"}}
        assert health_check_warning(data) == []


class TestEvaluatePolicies:
    def test_dev_no_replica_check(self):
        data = {"service": {"image": "app:1.0", "replicas": 1, "health_check": "/h"}}
        issues = evaluate_policies(data, environment="dev")
        rules = [i.rule for i in issues]
        assert "minimum_replicas" not in rules

    def test_prod_includes_replica_check(self):
        data = {"service": {"image": "app:1.0", "replicas": 1, "health_check": "/h"}}
        issues = evaluate_policies(data, environment="prod")
        rules = [i.rule for i in issues]
        assert "minimum_replicas" in rules

    def test_clean_config_passes(self):
        data = {
            "service": {
                "image": "app:1.0",
                "replicas": 3,
                "port": 8080,
                "health_check": "/health",
            }
        }
        issues = evaluate_policies(data, environment="prod")
        errors = [i for i in issues if i.severity.value == "error"]
        assert errors == []
