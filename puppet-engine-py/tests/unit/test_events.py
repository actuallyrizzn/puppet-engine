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
    
    # Start the engine
    await engine.start()
    
    # Wait for event processing
    await asyncio.sleep(0.1)
    
    # Stop the engine
    await engine.stop()
    await asyncio.sleep(0.1)
    
    assert "test" in results

@pytest.mark.asyncio
async def test_event_engine_scheduled_events():
    engine = EventEngine()
    results = []
    
    async def listener(event):
        results.append(event.type)
    
    engine.add_event_listener("scheduled", listener)
    
    # Test that we can schedule an event without timing issues
    from datetime import datetime, timedelta
    scheduled_time = datetime.utcnow() + timedelta(seconds=0.1)
    event = Event(type="scheduled", agent_id="a", data={}, scheduled_for=scheduled_time)
    engine.schedule_event(event)
    
    # Verify the event was scheduled
    assert len(engine.scheduled_events) == 1
    assert engine.scheduled_events[0].type == "scheduled"

@pytest.mark.asyncio
async def test_event_engine_sync_listener():
    engine = EventEngine()
    results = []
    
    def sync_listener(event):
        results.append(event.type)
    
    engine.add_event_listener("sync_test", sync_listener)
    event = Event(type="sync_test", agent_id="a", data={})
    engine.queue_event(event)
    
    # Start the engine
    await engine.start()
    
    # Wait for event processing
    await asyncio.sleep(0.1)
    
    # Stop the engine
    await engine.stop()
    await asyncio.sleep(0.1)
    
    assert "sync_test" in results

def test_event_priority_enum():
    assert EventPriority.LOW.value == 0
    assert EventPriority.NORMAL.value == 1
    assert EventPriority.HIGH.value == 2
    assert EventPriority.CRITICAL.value == 3 