#!/usr/bin/env python3
"""
Test script to verify SQLite migration is working correctly.
"""

import asyncio
import os
from src.memory.sqlite_store import SQLiteMemoryStore
from src.core.models import MemoryItem, MemoryType
from datetime import datetime

async def test_sqlite_migration():
    """Test the SQLite memory store functionality."""
    print("🧪 Testing SQLite Migration...")
    
    # Clean up any existing test database
    test_db = "test_puppet_engine.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Create SQLite memory store
    memory_store = SQLiteMemoryStore(test_db)
    
    try:
        # Test 1: Store a memory
        print("📝 Testing memory storage...")
        memory = MemoryItem(
            agent_id="test-agent",
            type=MemoryType.CORE,
            content="This is a test memory for SQLite migration",
            metadata={"test": True, "migration": "sqlite"},
            importance=5.0
        )
        
        memory_id = await memory_store.store_memory(memory)
        print(f"✅ Memory stored with ID: {memory_id}")
        
        # Test 2: Retrieve the memory
        print("🔍 Testing memory retrieval...")
        retrieved_memory = await memory_store.get_memory(memory_id)
        if retrieved_memory:
            print(f"✅ Memory retrieved: {retrieved_memory.content}")
            print(f"   Agent ID: {retrieved_memory.agent_id}")
            print(f"   Type: {retrieved_memory.type}")
            print(f"   Importance: {retrieved_memory.importance}")
        else:
            print("❌ Failed to retrieve memory")
            return False
        
        # Test 3: Search memories
        print("🔎 Testing memory search...")
        search_results = await memory_store.search_memories("test-agent", "SQLite", limit=5)
        print(f"✅ Found {len(search_results)} memories containing 'SQLite'")
        
        # Test 4: Get agent memories
        print("👤 Testing agent memories retrieval...")
        agent_memories = await memory_store.get_agent_memories("test-agent", limit=10)
        print(f"✅ Found {len(agent_memories)} memories for test-agent")
        
        # Test 5: Update memory
        print("✏️ Testing memory update...")
        update_result = await memory_store.update_memory(memory_id, {
            "content": "This memory has been updated for SQLite migration",
            "importance": 8.0
        })
        if update_result:
            print(f"✅ Memory updated: {update_result.content}")
            print(f"   New importance: {update_result.importance}")
        else:
            print("❌ Failed to update memory")
            return False
        
        # Test 6: Store multiple memories
        print("📚 Testing multiple memory storage...")
        for i in range(5):
            memory = MemoryItem(
                agent_id="test-agent",
                type=MemoryType.EVENT,
                content=f"Event memory {i+1} for SQLite testing",
                metadata={"event_id": i+1},
                importance=float(i+1)
            )
            await memory_store.store_memory(memory)
        print("✅ Stored 5 additional memories")
        
        # Test 7: Get memories by type
        print("🏷️ Testing memory filtering by type...")
        event_memories = await memory_store.get_agent_memories("test-agent", MemoryType.EVENT, limit=10)
        print(f"✅ Found {len(event_memories)} event memories")
        
        # Test 8: Delete memory
        print("🗑️ Testing memory deletion...")
        delete_result = await memory_store.delete_memory(memory_id)
        if delete_result:
            print("✅ Memory deleted successfully")
        else:
            print("❌ Failed to delete memory")
            return False
        
        # Verify deletion
        deleted_memory = await memory_store.get_memory(memory_id)
        if deleted_memory is None:
            print("✅ Memory deletion verified")
        else:
            print("❌ Memory still exists after deletion")
            return False
        
        print("\n🎉 All SQLite migration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Clean up
        await memory_store.close()
        if os.path.exists(test_db):
            os.remove(test_db)
        print("🧹 Test database cleaned up")

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_sqlite_migration())
    if success:
        print("\n✅ SQLite Migration Test: PASSED")
        exit(0)
    else:
        print("\n❌ SQLite Migration Test: FAILED")
        exit(1) 