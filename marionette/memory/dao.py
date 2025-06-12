import aiosqlite
from typing import List, Optional
from marionette.types import MemoryItem, Relationship

DB_PATH = 'marionette.db'

CREATE_TABLES_SQL = [
    '''CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )''',
    '''CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(agent_id) REFERENCES agents(id)
    )''',
    '''CREATE TABLE IF NOT EXISTS relationships (
        agent_id INTEGER NOT NULL,
        target_id INTEGER NOT NULL,
        relationship_type TEXT NOT NULL,
        strength REAL NOT NULL,
        PRIMARY KEY(agent_id, target_id)
    )'''
]

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        for sql in CREATE_TABLES_SQL:
            await db.execute(sql)
        await db.commit()

async def insert_memory(memory: MemoryItem):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO memories (agent_id, content, timestamp) VALUES (?, ?, ?)',
            (memory.agent_id, memory.content, memory.timestamp)
        )
        await db.commit()

async def get_memories(agent_id: int) -> List[MemoryItem]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id, agent_id, content, timestamp FROM memories WHERE agent_id = ?',
            (agent_id,)
        )
        rows = await cursor.fetchall()
        return [MemoryItem(*row) for row in rows]

async def insert_relationship(rel: Relationship):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR REPLACE INTO relationships (agent_id, target_id, relationship_type, strength) VALUES (?, ?, ?, ?)',
            (rel.agent_id, rel.target_id, rel.relationship_type, rel.strength)
        )
        await db.commit()

async def get_relationships(agent_id: int) -> List[Relationship]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT agent_id, target_id, relationship_type, strength FROM relationships WHERE agent_id = ?',
            (agent_id,)
        )
        rows = await cursor.fetchall()
        return [Relationship(*row) for row in rows] 