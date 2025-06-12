import pytest
import asyncio
from marionette.events.event import Event, EventRouter

@pytest.mark.asyncio
async def test_event_router():
    router = EventRouter()
    called = {}

    async def handler(event):
        called[event.type] = event.payload

    router.register("test", handler)
    event = Event(id=1, type="test", payload={"foo": "bar"}, timestamp="2024-01-01T00:00:00Z")
    await router.trigger(event)
    assert called["test"] == {"foo": "bar"} 