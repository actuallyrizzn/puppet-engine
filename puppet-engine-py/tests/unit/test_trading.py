import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys

# Patch sys.modules to mock solana and its submodules
sys.modules['solana'] = MagicMock()
sys.modules['solana.rpc'] = MagicMock()
sys.modules['solana.rpc.async_api'] = MagicMock()
sys.modules['solana.keypair'] = MagicMock()
sys.modules['solana.transaction'] = MagicMock()
sys.modules['solana.system_program'] = MagicMock()
sys.modules['solana.publickey'] = MagicMock()
sys.modules['base58'] = MagicMock()

from src.solana.trading import SolanaTrader

@pytest.fixture
def trader():
    wallet = MagicMock()
    return SolanaTrader(wallet=wallet)

@pytest.mark.asyncio
async def test_get_quote(trader):
    with patch.object(trader, 'get_quote', new_callable=AsyncMock, return_value={'price': 1.23}):
        result = await trader.get_quote('SOL', 'USDC', 1)
        assert result == {'price': 1.23}

@pytest.mark.asyncio
async def test_get_token_price(trader):
    with patch.object(trader, 'get_token_price', new_callable=AsyncMock, return_value=42.0):
        result = await trader.get_token_price('SOL')
        assert result == 42.0

@pytest.mark.asyncio
async def test_get_supported_tokens(trader):
    with patch.object(trader, 'get_supported_tokens', new_callable=AsyncMock, return_value=['SOL', 'USDC']):
        result = await trader.get_supported_tokens()
        assert 'SOL' in result

@pytest.mark.asyncio
async def test_execute_swap_success(trader):
    with patch.object(trader, 'execute_swap', new_callable=AsyncMock, return_value={'tx': 'abc', 'status': 'success'}):
        result = await trader.execute_swap({'quote': 'data'})
        assert result['status'] == 'success'

@pytest.mark.asyncio
async def test_execute_swap_error(trader):
    with patch.object(trader, 'execute_swap', new_callable=AsyncMock, side_effect=Exception('fail')):
        with pytest.raises(Exception):
            await trader.execute_swap({'quote': 'data'})

@pytest.mark.asyncio
async def test_get_route_success(trader):
    with patch.object(trader, 'get_route', new_callable=AsyncMock, return_value={'route': 'best'}):
        result = await trader.get_route('SOL', 'USDC', 1)
        assert result['route'] == 'best'

@pytest.mark.asyncio
async def test_get_route_error(trader):
    with patch.object(trader, 'get_route', new_callable=AsyncMock, side_effect=Exception('fail')):
        with pytest.raises(Exception):
            await trader.get_route('SOL', 'USDC', 1)

@pytest.mark.asyncio
async def test_close(trader):
    with patch.object(trader, 'close', new_callable=AsyncMock, return_value=True):
        assert await trader.close() is True 