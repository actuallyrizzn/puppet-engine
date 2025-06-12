from pydantic import BaseModel
from typing import Dict, Any, Callable, List

class Event(BaseModel):
    id: int
    type: str
    payload: Dict[str, Any]
    timestamp: str

class EventRouter:
    def __init__(self):
        self.handlers: Dict[str, List[Callable[[Event], None]]] = {}

    def register(self, event_type: str, handler: Callable[[Event], None]):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def trigger(self, event: Event):
        for handler in self.handlers.get(event.type, []):
            await handler(event) 