#!/usr/bin/env python3
"""
Test script to verify SQLite vector store functionality.
"""

import asyncio
import os
import numpy as np
from src.memory.sqlite_store import SQLiteMemoryStore
from src.memory.sqlite_vector_store import SQLiteVectorStore
from src.core.models import MemoryItem, MemoryType
from datetime import datetime

async def test_sqlite_vector_store():
    """Test the SQLite vector store functionality."""
    print("🧪 Testing SQLite Vector Store...")
    
    # Clean up any existing test database
    test_db = "test_vector_store.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Create SQLite memory store and vector store
    memory_store = SQLiteMemoryStore(test_db)
    vector_store = SQLiteVectorStore(test_db)
    
    try:
        # Test 1: Store a memory with embedding
        print("📝 Testing memory storage with embedding...")
        memory = MemoryItem(
            agent_id="test-agent",
            type=MemoryType.CORE,
            content="This is a test memory with vector embedding",
            metadata={"test": True, "vector": True},
            importance=5.0,
            vector_embedding=[0.1, 0.2, 0.3, 0.4, 0.5]
        )
        
        memory_id = await memory_store.store_memory(memory)
        print(f"✅ Memory stored with ID: {memory_id}")
        
        # Test 2: Store embedding separately
        print("🔢 Testing embedding storage...")
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        embedding_stored = await vector_store.store_embedding(memory_id, embedding)
        if embedding_stored:
            print("✅ Embedding stored successfully")
        else:
            print("❌ Failed to store embedding")
            return False
        
        # Test 3: Store multiple memories with embeddings
        print("📚 Testing multiple embeddings...")
        embeddings = []
        for i in range(5):
            # Create memory
            memory = MemoryItem(
                agent_id="test-agent",
                type=MemoryType.EVENT,
                content=f"Event memory {i+1} with embedding",
                metadata={"event_id": i+1},
                importance=float(i+1)
            )
            memory_id = await memory_store.store_memory(memory)
            
            # Create embedding (similar but slightly different)
            embedding = [0.1 + i*0.1, 0.2 + i*0.05, 0.3 + i*0.02, 0.4, 0.5]
            embeddings.append((memory_id, embedding))
            
            # Store embedding
            await vector_store.store_embedding(memory_id, embedding)
        
        print(f"✅ Stored {len(embeddings)} additional embeddings")
        
        # Test 4: Search similar embeddings
        print("🔍 Testing similarity search...")
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        similar_results = await vector_store.search_similar(query_embedding, limit=10)
        
        if similar_results:
            print(f"✅ Found {len(similar_results)} similar embeddings")
            for i, result in enumerate(similar_results[:3]):  # Show top 3
                print(f"   {i+1}. Memory ID: {result['memory_id']}, Similarity: {result['similarity']:.4f}")
        else:
            print("❌ No similar embeddings found")
            return False
        
        # Test 5: Search with agent filter
        print("👤 Testing agent-filtered search...")
        agent_results = await vector_store.search_similar(query_embedding, agent_id="test-agent", limit=5)
        print(f"✅ Found {len(agent_results)} embeddings for test-agent")
        
        # Test 6: Test cosine similarity calculation
        print("📐 Testing cosine similarity...")
        # Create two very similar embeddings
        embedding1 = [1.0, 0.0, 0.0, 0.0, 0.0]
        embedding2 = [0.9, 0.1, 0.0, 0.0, 0.0]
        
        # Store them
        memory1 = MemoryItem(
            agent_id="test-agent",
            type=MemoryType.CORE,
            content="Test embedding 1",
            importance=1.0
        )
        memory2 = MemoryItem(
            agent_id="test-agent",
            type=MemoryType.CORE,
            content="Test embedding 2",
            importance=1.0
        )
        
        mem_id1 = await memory_store.store_memory(memory1)
        mem_id2 = await memory_store.store_memory(memory2)
        
        await vector_store.store_embedding(mem_id1, embedding1)
        await vector_store.store_embedding(mem_id2, embedding2)
        
        # Search with embedding1 as query
        similarity_results = await vector_store.search_similar(embedding1, limit=5)
        if similarity_results:
            print(f"✅ Similarity search returned {len(similarity_results)} results")
            # The first result should be the most similar (embedding1 itself)
            top_result = similarity_results[0]
            print(f"   Top similarity: {top_result['similarity']:.4f}")
        else:
            print("❌ Similarity search failed")
            return False
        
        # Test 7: Delete embedding
        print("🗑️ Testing embedding deletion...")
        delete_result = await vector_store.delete_embedding(mem_id1)
        if delete_result:
            print("✅ Embedding deleted successfully")
        else:
            print("❌ Failed to delete embedding")
            return False
        
        # Verify deletion by searching again
        search_after_delete = await vector_store.search_similar(embedding1, limit=5)
        deleted_found = any(result['memory_id'] == mem_id1 for result in search_after_delete)
        if not deleted_found:
            print("✅ Embedding deletion verified")
        else:
            print("❌ Deleted embedding still found in search")
            return False
        
        print("\n🎉 All SQLite vector store tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        await memory_store.close()
        await vector_store.close()
        if os.path.exists(test_db):
            os.remove(test_db)
        print("🧹 Test database cleaned up")

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_sqlite_vector_store())
    if success:
        print("\n✅ SQLite Vector Store Test: PASSED")
        exit(0)
    else:
        print("\n❌ SQLite Vector Store Test: FAILED")
        exit(1) 