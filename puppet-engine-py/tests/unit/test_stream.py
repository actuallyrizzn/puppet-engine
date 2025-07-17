import pytest
from unittest.mock import patch, MagicMock
from src.twitter.stream import TwitterStream

@pytest.fixture
def stream():
    return TwitterStream(auth=MagicMock())

def test_start_stream(stream):
    with patch.object(stream, 'connect', return_value=True) as mock_connect:
        result = stream.start()
        assert result is True
        mock_connect.assert_called()

def test_stop_stream(stream):
    with patch.object(stream, 'disconnect', return_value=True) as mock_disconnect:
        result = stream.stop()
        assert result is True
        mock_disconnect.assert_called()

def test_on_data(stream):
    with patch.object(stream, 'process_data', return_value=True) as mock_process:
        result = stream.on_data({'data': 'test'})
        assert result is True
        mock_process.assert_called()

def test_error_handling(stream):
    with patch.object(stream, 'connect', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            stream.start() 