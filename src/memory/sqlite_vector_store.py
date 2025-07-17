import aiosqlite
import json
import numpy as np
from typing import List, Dict, Any, Optional
from .base import VectorStore
from datetime import datetime

class SQLiteVectorStore(VectorStore):
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
        
        # Create embeddings table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                memory_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                embedding_data TEXT NOT NULL,
                embedding_dimension INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (memory_id) REFERENCES memories (id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for better performance
        await db.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_agent_id ON embeddings(agent_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_dimension ON embeddings(embedding_dimension)")
        
        await db.commit()

    async def store_embedding(self, memory_id: str, embedding: List[float]) -> bool:
        """Store an embedding for a memory item."""
        try:
            db = await self._get_db()
            
            # Get agent_id from the memory
            async with db.execute("SELECT agent_id FROM memories WHERE id = ?", (memory_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return False
                agent_id = row[0]
            
            # Store the embedding
            embedding_json = json.dumps(embedding)
            embedding_dimension = len(embedding)
            
            await db.execute("""
                INSERT OR REPLACE INTO embeddings (memory_id, agent_id, embedding_data, embedding_dimension, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                memory_id,
                agent_id,
                embedding_json,
                embedding_dimension,
                datetime.utcnow().isoformat()
            ))
            
            await db.commit()
            return True
            
        except Exception as e:
            print(f"Error storing embedding: {e}")
            return False

    async def search_similar(self, query_embedding: List[float], agent_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar embeddings using cosine similarity."""
        try:
            db = await self._get_db()
            
            # Get all embeddings
            if agent_id:
                async with db.execute("""
                    SELECT memory_id, agent_id, embedding_data, embedding_dimension
                    FROM embeddings WHERE agent_id = ?
                """, (agent_id,)) as cursor:
                    rows = await cursor.fetchall()
            else:
                async with db.execute("""
                    SELECT memory_id, agent_id, embedding_data, embedding_dimension
                    FROM embeddings
                """) as cursor:
                    rows = await cursor.fetchall()
            
            if not rows:
                return []
            
            # Calculate similarities
            similarities = []
            query_embedding_array = np.array(query_embedding)
            
            for row in rows:
                memory_id, row_agent_id, embedding_json, dimension = row
                
                # Skip if dimensions don't match
                if dimension != len(query_embedding):
                    continue
                
                try:
                    stored_embedding = np.array(json.loads(embedding_json))
                    
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(query_embedding_array, stored_embedding)
                    
                    similarities.append({
                        'memory_id': memory_id,
                        'agent_id': row_agent_id,
                        'similarity': similarity,
                        'embedding_dimension': dimension
                    })
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Error processing embedding for memory {memory_id}: {e}")
                    continue
            
            # Sort by similarity (descending) and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            print(f"Error searching embeddings: {e}")
            return []

    async def delete_embedding(self, memory_id: str) -> bool:
        """Delete an embedding for a memory item."""
        try:
            db = await self._get_db()
            
            async with db.execute("DELETE FROM embeddings WHERE memory_id = ?", (memory_id,)) as cursor:
                await db.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting embedding: {e}")
            return False

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0

    async def close(self):
        """Close the database connection."""
        if self._db:
            await self._db.close()
            self._db = None 