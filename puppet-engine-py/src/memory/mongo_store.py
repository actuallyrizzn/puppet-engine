import motor.motor_asyncio
from typing import List, Dict, Any, Optional
from .base import MemoryStore
from ..core.models import MemoryItem, MemoryType
from datetime import datetime

class MongoMemoryStore(MemoryStore):
    def __init__(self, mongodb_uri: str, db_name: str = "puppet_engine"):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_uri)
        self.db = self.client[db_name]
        self.memories = self.db.agent_memories

    async def store_memory(self, memory: MemoryItem) -> str:
        doc = memory.dict()
        doc["timestamp"] = doc.get("timestamp") or datetime.utcnow()
        result = await self.memories.insert_one(doc)
        return str(result.inserted_id)

    async def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        from bson import ObjectId
        doc = await self.memories.find_one({"_id": ObjectId(memory_id)})
        if doc:
            doc["id"] = str(doc["_id"])
            return MemoryItem(**doc)
        return None

    async def search_memories(self, agent_id: str, query: str, limit: int = 10) -> List[MemoryItem]:
        cursor = self.memories.find({"agent_id": agent_id, "content": {"$regex": query, "$options": "i"}}).sort("timestamp", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [MemoryItem(**doc) for doc in docs]

    async def get_agent_memories(self, agent_id: str, memory_type: Optional[MemoryType] = None, limit: int = 50) -> List[MemoryItem]:
        query = {"agent_id": agent_id}
        if memory_type:
            query["type"] = memory_type.value
        cursor = self.memories.find(query).sort("timestamp", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [MemoryItem(**doc) for doc in docs]

    async def delete_memory(self, memory_id: str) -> bool:
        from bson import ObjectId
        result = await self.memories.delete_one({"_id": ObjectId(memory_id)})
        return result.deleted_count > 0

    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> Optional[MemoryItem]:
        from bson import ObjectId
        await self.memories.update_one({"_id": ObjectId(memory_id)}, {"$set": updates})
        return await self.get_memory(memory_id) 