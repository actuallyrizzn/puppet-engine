import aiosqlite
import json
from typing import List, Dict, Any, Optional
from .base import MemoryStore
from ..core.models import MemoryItem, MemoryType
from datetime import datetime
import uuid

class SQLiteMemoryStore(MemoryStore):
    def __init__(self, db_path: str = "puppet_engine.db"):
        self.db_path = db_path
        self._db = None

    async def _get_db(self) -> aiosqlite.Connection:
        """Get or create database connection."""
        if self._db is None:
            self._db = await aiosqlite.connect(self.db_path)
            await self._db.execute("PRAGMA foreign_keys = ON")
            await self._create_tables()
        return self._db

    async def _create_tables(self):
        """Create the necessary tables if they don't exist."""
        db = await self._get_db()
        
        # Create memories table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                importance REAL NOT NULL DEFAULT 1.0,
                vector_embedding TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create indexes for better performance
        await db.execute("CREATE INDEX IF NOT EXISTS idx_memories_agent_id ON memories(agent_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_memories_agent_type ON memories(agent_id, type)")
        
        await db.commit()

    async def store_memory(self, memory: MemoryItem) -> str:
        """Store a memory item and return its ID."""
        db = await self._get_db()
        
        # Generate ID if not provided
        memory_id = memory.id or str(uuid.uuid4())
        
        # Prepare data
        metadata_json = json.dumps(memory.metadata)
        vector_embedding_json = json.dumps(memory.vector_embedding) if memory.vector_embedding else None
        timestamp = memory.timestamp.isoformat() if memory.timestamp else datetime.utcnow().isoformat()
        
        await db.execute("""
            INSERT INTO memories (id, agent_id, type, content, metadata, timestamp, importance, vector_embedding, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id,
            memory.agent_id,
            memory.type.value,
            memory.content,
            metadata_json,
            timestamp,
            memory.importance,
            vector_embedding_json,
            datetime.utcnow().isoformat()
        ))
        
        await db.commit()
        return memory_id

    async def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item by ID."""
        db = await self._get_db()
        
        async with db.execute("""
            SELECT id, agent_id, type, content, metadata, timestamp, importance, vector_embedding
            FROM memories WHERE id = ?
        """, (memory_id,)) as cursor:
            row = await cursor.fetchone()
            
        if row:
            return self._row_to_memory_item(row)
        return None

    async def search_memories(self, agent_id: str, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search memories by content for a specific agent."""
        db = await self._get_db()
        
        async with db.execute("""
            SELECT id, agent_id, type, content, metadata, timestamp, importance, vector_embedding
            FROM memories 
            WHERE agent_id = ? AND content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (agent_id, f"%{query}%", limit)) as cursor:
            rows = await cursor.fetchall()
            
        return [self._row_to_memory_item(row) for row in rows]

    async def get_agent_memories(self, agent_id: str, memory_type: Optional[MemoryType] = None, limit: int = 50) -> List[MemoryItem]:
        """Get memories for a specific agent, optionally filtered by type."""
        db = await self._get_db()
        
        if memory_type:
            async with db.execute("""
                SELECT id, agent_id, type, content, metadata, timestamp, importance, vector_embedding
                FROM memories 
                WHERE agent_id = ? AND type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_id, memory_type.value, limit)) as cursor:
                rows = await cursor.fetchall()
        else:
            async with db.execute("""
                SELECT id, agent_id, type, content, metadata, timestamp, importance, vector_embedding
                FROM memories 
                WHERE agent_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_id, limit)) as cursor:
                rows = await cursor.fetchall()
                
        return [self._row_to_memory_item(row) for row in rows]

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item by ID."""
        db = await self._get_db()
        
        async with db.execute("DELETE FROM memories WHERE id = ?", (memory_id,)) as cursor:
            await db.commit()
            return cursor.rowcount > 0

    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> Optional[MemoryItem]:
        """Update a memory item with new data."""
        db = await self._get_db()
        
        # Build update query dynamically
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key == 'metadata':
                set_clauses.append("metadata = ?")
                values.append(json.dumps(value))
            elif key == 'vector_embedding':
                set_clauses.append("vector_embedding = ?")
                values.append(json.dumps(value) if value else None)
            elif key == 'timestamp':
                set_clauses.append("timestamp = ?")
                values.append(value.isoformat() if hasattr(value, 'isoformat') else value)
            elif key in ['agent_id', 'type', 'content', 'importance']:
                set_clauses.append(f"{key} = ?")
                values.append(value.value if hasattr(value, 'value') else value)
        
        if not set_clauses:
            return await self.get_memory(memory_id)
        
        values.append(memory_id)
        query = f"UPDATE memories SET {', '.join(set_clauses)} WHERE id = ?"
        
        async with db.execute(query, values) as cursor:
            await db.commit()
            
        return await self.get_memory(memory_id)

    def _row_to_memory_item(self, row) -> MemoryItem:
        """Convert a database row to a MemoryItem."""
        memory_id, agent_id, memory_type, content, metadata_json, timestamp, importance, vector_embedding_json = row
        
        # Parse JSON fields
        metadata = json.loads(metadata_json) if metadata_json else {}
        vector_embedding = json.loads(vector_embedding_json) if vector_embedding_json else None
        
        # Parse timestamp
        try:
            timestamp_dt = datetime.fromisoformat(timestamp)
        except (ValueError, TypeError):
            timestamp_dt = datetime.utcnow()
        
        return MemoryItem(
            id=memory_id,
            agent_id=agent_id,
            type=MemoryType(memory_type),
            content=content,
            metadata=metadata,
            timestamp=timestamp_dt,
            importance=importance,
            vector_embedding=vector_embedding
        )

    async def close(self):
        """Close the database connection."""
        if self._db:
            await self._db.close()
            self._db = None 