import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.solana.trading import SolanaTrader

@pytest.fixture
def trader():
    return SolanaTrader(rpc_url='http://localhost', keypair=MagicMock())

def test_get_quote(trader):
    with patch.object(trader, 'fetch_quote', return_value={'price': 1.23}):
        result = trader.get_quote('SOL', 'USDC', 1)
        assert result == {'price': 1.23}

def test_get_token_price(trader):
    with patch.object(trader, 'fetch_token_price', return_value=42.0):
        result = trader.get_token_price('SOL')
        assert result == 42.0

def test_get_supported_tokens(trader):
    with patch.object(trader, 'fetch_supported_tokens', return_value=['SOL', 'USDC']):
        result = trader.get_supported_tokens()
        assert 'SOL' in result

def test_execute_swap_success(trader):
    with patch.object(trader, 'execute_swap', return_value={'tx': 'abc', 'status': 'success'}):
        result = trader.execute_swap('SOL', 'USDC', 1)
        assert result['status'] == 'success'

def test_execute_swap_error(trader):
    with patch.object(trader, 'execute_swap', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            trader.execute_swap('SOL', 'USDC', 1)

def test_get_route_success(trader):
    with patch.object(trader, 'get_route', return_value={'route': 'best'}):
        result = trader.get_route('SOL', 'USDC', 1)
        assert result['route'] == 'best'

def test_get_route_error(trader):
    with patch.object(trader, 'get_route', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            trader.get_route('SOL', 'USDC', 1)

def test_close(trader):
    with patch.object(trader, 'close', return_value=True):
        assert trader.close() is True 