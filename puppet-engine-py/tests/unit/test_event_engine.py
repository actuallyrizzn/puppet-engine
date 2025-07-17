import pytest
import asyncio
from src.events.engine import EventEngine, EventPriority
from src.core.models import Event

@pytest.mark.asyncio
async def test_event_engine_queue_and_listener():
    engine = EventEngine()
    results = []
    
    async def listener(event):
        results.append(event.type)
    
    engine.add_event_listener("test", listener)
    event = Event(type="test", agent_id="a", data={})
    engine.queue_event(event)
    
    try:
        # Start the engine
        await engine.start()
        
        # Wait for event processing
        await asyncio.sleep(0.1)
        
        assert "test" in results
    finally:
        # Always stop the engine to clean up background tasks
        await engine.stop()
        # Give tasks time to cancel
        await asyncio.sleep(0.1) 