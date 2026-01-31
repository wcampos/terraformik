"""Pytest configuration and shared fixtures."""
import pytest


@pytest.fixture
def valid_app_names():
    """Valid app names (lowercase, numbers, hyphens)."""
    return ["myapp", "app1", "my-app", "myapp2", "a"]


@pytest.fixture
def invalid_app_names():
    """Invalid app names."""
    return ["MyApp", "my_app", "my.app", "APP", "", "my app", "myapp!"]


@pytest.fixture
def valid_environments():
    """Valid environment names."""
    return ["dev", "staging", "prod"]


@pytest.fixture
def invalid_environments():
    """Invalid environment names."""
    return ["development", "production", "test", "prodution", ""]
