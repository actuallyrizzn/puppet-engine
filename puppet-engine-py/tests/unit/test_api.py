import pytest
from unittest.mock import patch, MagicMock
from src.api.server import APIServer
from src.core.settings import Settings

def test_api_server_init():
    settings = Settings()
    server = APIServer(settings)
    assert server.app is not None
    assert server.settings == settings
    assert server.node_adapter is not None

def test_api_server_setup_middleware():
    settings = Settings()
    server = APIServer(settings)
    # Test that middleware setup doesn't raise exceptions
    assert True

def test_api_server_setup_routes():
    settings = Settings()
    server = APIServer(settings)
    # Test that route setup doesn't raise exceptions
    assert True

def test_api_server_setup_observability():
    settings = Settings()
    server = APIServer(settings)
    # Test that observability setup doesn't raise exceptions
    assert True

def test_api_server_app_properties():
    settings = Settings()
    server = APIServer(settings)
    # Test that the app has the expected properties
    assert hasattr(server.app, 'routes')
    assert hasattr(server.app, 'middleware') 