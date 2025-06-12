from typing import Dict, List, Optional, Callable, Any
import asyncio
from datetime import datetime
from ..types import Event, Agent
from ..agents.manager import agent_manager

class EventRouter:
    def __init__(self):
        self._handlers: Dict[str, List[Callable[[Event], Any]]] = {}
        self._agent_handlers: Dict[int, Dict[str, List[Callable[[Event], Any]]]] = {}
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the event processing loop."""
        self._processing_task = asyncio.create_task(self._process_events())
    
    async def stop(self):
        """Stop the event processing loop."""
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
    
    def register_handler(self, event_type: str, handler: Callable[[Event], Any]):
        """Register a global event handler."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def register_agent_handler(
        self,
        agent_id: int,
        event_type: str,
        handler: Callable[[Event], Any]
    ):
        """Register an event handler for a specific agent."""
        if agent_id not in self._agent_handlers:
            self._agent_handlers[agent_id] = {}
        if event_type not in self._agent_handlers[agent_id]:
            self._agent_handlers[agent_id][event_type] = []
        self._agent_handlers[agent_id][event_type].append(handler)
    
    async def dispatch_event(self, event: Event):
        """Dispatch an event to all relevant handlers."""
        await self._event_queue.put(event)
    
    async def _process_events(self):
        """Process events from the queue."""
        while True:
            try:
                event = await self._event_queue.get()
                
                # Get all handlers for this event type
                handlers = self._handlers.get(event.type, [])
                
                # Get agent-specific handlers if this is an agent event
                if "agent_id" in event.payload:
                    agent_id = event.payload["agent_id"]
                    agent_handlers = self._agent_handlers.get(agent_id, {}).get(event.type, [])
                    handlers.extend(agent_handlers)
                
                # Execute all handlers concurrently
                if handlers:
                    await asyncio.gather(
                        *(self._execute_handler(handler, event) for handler in handlers)
                    )
                
                self._event_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error processing event: {e}")
                continue
    
    async def _execute_handler(self, handler: Callable[[Event], Any], event: Event):
        """Execute a single event handler."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            print(f"Error in event handler: {e}")

# Global event router instance
event_router = EventRouter() 