from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..core.models import MemoryItem, MemoryType

class MemoryStore(ABC):
    @abstractmethod
    async def store_memory(self, memory: MemoryItem) -> str:
        pass

    @abstractmethod
    async def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        pass

    @abstractmethod
    async def search_memories(self, agent_id: str, query: str, limit: int = 10) -> List[MemoryItem]:
        pass

    @abstractmethod
    async def get_agent_memories(self, agent_id: str, memory_type: Optional[MemoryType] = None, limit: int = 50) -> List[MemoryItem]:
        pass

    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        pass

    @abstractmethod
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> Optional[MemoryItem]:
        pass

class VectorStore(ABC):
    @abstractmethod
    async def store_embedding(self, memory_id: str, embedding: List[float]) -> bool:
        pass

    @abstractmethod
    async def search_similar(self, query_embedding: List[float], agent_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete_embedding(self, memory_id: str) -> bool:
        pass 