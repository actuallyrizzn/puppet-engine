import asyncio
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime, timedelta
from enum import Enum
import heapq
from ..core.models import Event

class EventPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class EventEngine:
    def __init__(self):
        self.event_queue: List[Event] = []
        self.event_listeners: Dict[str, List[Callable[[Event], Any]]] = {}
        self.scheduled_events: List[Event] = []
        self.is_processing = False
        self.event_history: List[Event] = []

    async def start(self):
        """Start event processing loop."""
        self.is_processing = True
        asyncio.create_task(self._process_events())
        asyncio.create_task(self._check_scheduled_events())

    async def _process_events(self):
        """Main event processing loop."""
        while self.is_processing:
            if self.event_queue:
                event = self.event_queue.pop(0)
                await self._dispatch_event(event)
                self.event_history.append(event)
                if len(self.event_history) > 1000:
                    self.event_history = self.event_history[-500:]
            else:
                await asyncio.sleep(0.1)

    async def _check_scheduled_events(self):
        """Check and enqueue scheduled events."""
        while self.is_processing:
            now = datetime.utcnow()
            ready = [e for e in self.scheduled_events if e.scheduled_for and e.scheduled_for <= now]
            for event in ready:
                self.event_queue.append(event)
                self.scheduled_events.remove(event)
            await asyncio.sleep(1)

    def add_event_listener(self, event_type: str, listener: Callable[[Event], Any]):
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(listener)

    async def _dispatch_event(self, event: Event):
        listeners = self.event_listeners.get(event.type, [])
        for listener in listeners:
            if asyncio.iscoroutinefunction(listener):
                await listener(event)
            else:
                listener(event)

    def schedule_event(self, event: Event):
        self.scheduled_events.append(event)

    def queue_event(self, event: Event):
        self.event_queue.append(event)

    def stop(self):
        self.is_processing = False 