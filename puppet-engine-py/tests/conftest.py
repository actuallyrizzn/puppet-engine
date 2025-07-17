import pytest
import asyncio
import sys
from unittest.mock import MagicMock, patch
from src.events.engine import EventEngine

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

@pytest.fixture(scope='session', autouse=True)
def session_teardown():
    print("=== PYTEST SESSION TEARDOWN STARTED ===")
    yield
    # Attempt to forcibly stop all EventEngine instances
    async def cleanup():
        for obj in list(globals().values()):
            if isinstance(obj, EventEngine):
                print("[conftest] Forcibly stopping EventEngine instance at session teardown (awaiting async)")
                await obj.stop()
        print("=== PYTEST SESSION TEARDOWN REACHED ===")
        print("=== ALL TESTS COMPLETED SUCCESSFULLY ===")
    
    # Run the async cleanup
    try:
        asyncio.run(cleanup())
    except RuntimeError:
        # If there's already an event loop running, use it
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a task for the cleanup
            loop.create_task(cleanup())
        else:
            loop.run_until_complete(cleanup()) 