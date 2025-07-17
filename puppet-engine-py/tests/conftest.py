import pytest
import asyncio
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope='session')
def mock_solana_modules():
    with patch.dict('sys.modules', {
        'solana.rpc.async_api': MagicMock(),
        'solana.keypair': MagicMock(),
        'solana.transaction': MagicMock(),
        'solana.system_program': MagicMock(),
        'solana.publickey': MagicMock(),
        'base58': MagicMock(),
    }):
        yield 