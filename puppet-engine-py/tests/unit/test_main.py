import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from src.main import PuppetEngine, main, signal_handler
import signal

@pytest.fixture
def engine():
    return PuppetEngine()

def test_engine_init(engine):
    assert isinstance(engine.settings, object)
    assert hasattr(engine, 'logger')
    assert engine.components == {}
    assert engine.is_running is False
    assert engine._periodic_tasks == []

@pytest.mark.asyncio
async def test_initialize_success(engine):
    with patch('src.main.SQLiteMemoryStore'), \
         patch('src.main.TwitterXClient'), \
         patch('src.main.OpenAILLMProvider'), \
         patch('src.main.FakeLLMProvider'), \
         patch('src.main.EventEngine'), \
         patch('src.main.AgentManager') as MockAgentManager, \
         patch('src.main.APIServer'):
        mock_agent_manager = MockAgentManager.return_value
        mock_agent_manager.load_agents = AsyncMock()
        components = await engine.initialize()
        assert 'twitter_client' in components
        assert 'llm_providers' in components
        assert 'memory_store' in components
        assert 'event_engine' in components
        assert 'agent_manager' in components
        assert 'api_server' in components
        assert components['mongo_connected'] is True

@pytest.mark.asyncio
async def test_initialize_error(engine):
    with patch('src.main.SQLiteMemoryStore', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            await engine.initialize()

@pytest.mark.asyncio
async def test_start_and_shutdown(engine):
    # Patch all dependencies and methods
    with patch.object(engine, 'initialize', AsyncMock()), \
         patch.object(engine, '_setup_periodic_events'), \
         patch.object(engine, 'logger') as mock_logger:
        engine.initialize.return_value = {
            'event_engine': AsyncMock(start=AsyncMock()),
            'agent_manager': AsyncMock(start_streaming_mentions=AsyncMock(), agents={}),
            'mongo_connected': True
        }
        # Patch asyncio.sleep to break the loop
        with patch('asyncio.sleep', side_effect=[None, asyncio.CancelledError()]):
            with pytest.raises(asyncio.CancelledError):
                await engine.start()
        # Test shutdown
        engine._periodic_tasks = [AsyncMock(done=MagicMock(return_value=False), cancel=MagicMock())]
        engine.components = {'agent_manager': AsyncMock(stop_streaming_mentions=AsyncMock()),
                             'event_engine': AsyncMock(stop=AsyncMock()),
                             'twitter_client': AsyncMock(close=AsyncMock()),
                             'memory_store': MagicMock(client=MagicMock(close=MagicMock()))}
        await engine.shutdown()
        mock_logger.log.assert_any_call('info', 'Shutting down Puppet Engine...')


def test_signal_handler_triggers_shutdown():
    engine = MagicMock()
    with patch('src.main.engine_instance', engine):
        with patch('asyncio.create_task') as mock_create_task:
            signal_handler(signal.SIGINT, None)
            mock_create_task.assert_called()

@pytest.mark.asyncio
async def test_main_entrypoint():
    with patch('src.main.PuppetEngine') as MockEngine, \
         patch('src.main.signal.signal'), \
         patch('src.main.asyncio.run') as mock_run:
        await main()
        MockEngine.assert_called() 