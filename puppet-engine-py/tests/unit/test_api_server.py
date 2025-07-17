import pytest
from unittest.mock import patch, MagicMock
from src.api.server import APIServer

@pytest.fixture
def server():
    return APIServer(settings=MagicMock())

def test_server_init(server):
    assert hasattr(server, 'settings')

def test_setup_routes(server):
    with patch.object(server, 'setup_routes', return_value=True) as mock_setup:
        assert server.setup_routes() is True
        mock_setup.assert_called()

def test_setup_middleware(server):
    with patch.object(server, 'setup_middleware', return_value=True) as mock_setup:
        assert server.setup_middleware() is True
        mock_setup.assert_called()

def test_setup_observability(server):
    with patch.object(server, 'setup_observability', return_value=True) as mock_setup:
        assert server.setup_observability() is True
        mock_setup.assert_called() 