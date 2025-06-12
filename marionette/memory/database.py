import aiosqlite
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..config import settings

class SQLiteWriteQueue:
    def __init__(self, max_size: int = 1000, flush_interval: int = 60):
        self.queue: List[Dict[str, Any]] = []
        self.max_size = max_size
        self.flush_interval = flush_interval
        self._flush_task = None
        self._lock = asyncio.Lock()
    
    async def start(self):
        """Start the periodic flush task."""
        self._flush_task = asyncio.create_task(self._periodic_flush())
    
    async def stop(self):
        """Stop the periodic flush task and flush remaining items."""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        await self.flush()
    
    async def enqueue(self, item: Dict[str, Any]):
        """Add an item to the write queue."""
        async with self._lock:
            self.queue.append(item)
            if len(self.queue) >= self.max_size:
                await self.flush()
    
    async def _periodic_flush(self):
        """Periodically flush the queue."""
        while True:
            await asyncio.sleep(self.flush_interval)
            await self.flush()
    
    async def flush(self):
        """Flush all queued items to the database."""
        if not self.queue:
            return
        
        async with self._lock:
            items = self.queue.copy()
            self.queue.clear()
        
        async with aiosqlite.connect(settings.DATABASE_URL.replace("sqlite:///", "")) as db:
            for item in items:
                if item["type"] == "memory":
                    await db.execute(
                        "INSERT INTO memories (agent_id, content, timestamp) VALUES (?, ?, ?)",
                        (item["agent_id"], item["content"], item["timestamp"])
                    )
                elif item["type"] == "relationship":
                    await db.execute(
                        "INSERT INTO relationships (agent_id, target_id, relationship_type, strength) VALUES (?, ?, ?, ?)",
                        (item["agent_id"], item["target_id"], item["relationship_type"], item["strength"])
                    )
            await db.commit()

class Database:
    def __init__(self):
        self.write_queue = SQLiteWriteQueue(
            max_size=settings.MEMORY_QUEUE_SIZE,
            flush_interval=settings.MEMORY_FLUSH_INTERVAL
        )
    
    async def initialize(self):
        """Initialize the database schema."""
        async with aiosqlite.connect(settings.DATABASE_URL.replace("sqlite:///", "")) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    personality_name TEXT NOT NULL,
                    personality_description TEXT NOT NULL,
                    personality_traits TEXT NOT NULL,
                    style_guide_tone TEXT NOT NULL,
                    style_guide_language TEXT NOT NULL,
                    style_guide_quirks TEXT,
                    mood TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    strength REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id),
                    FOREIGN KEY (target_id) REFERENCES agents (id)
                )
            """)
            
            await db.commit()
        
        await self.write_queue.start()
    
    async def close(self):
        """Close the database connection and flush any remaining items."""
        await self.write_queue.stop()
    
    async def add_memory(self, agent_id: int, content: str):
        """Add a memory to the write queue."""
        await self.write_queue.enqueue({
            "type": "memory",
            "agent_id": agent_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def add_relationship(self, agent_id: int, target_id: int, relationship_type: str, strength: float):
        """Add a relationship to the write queue."""
        await self.write_queue.enqueue({
            "type": "relationship",
            "agent_id": agent_id,
            "target_id": target_id,
            "relationship_type": relationship_type,
            "strength": strength
        })
    
    async def get_agent_memories(self, agent_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve memories for an agent."""
        async with aiosqlite.connect(settings.DATABASE_URL.replace("sqlite:///", "")) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM memories WHERE agent_id = ? ORDER BY timestamp DESC LIMIT ?",
                (agent_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_agent_relationships(self, agent_id: int) -> List[Dict[str, Any]]:
        """Retrieve relationships for an agent."""
        async with aiosqlite.connect(settings.DATABASE_URL.replace("sqlite:///", "")) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM relationships WHERE agent_id = ?",
                (agent_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

# Global database instance
db = Database() 