#!/usr/bin/env python3
"""
Debug script to isolate the hanging issue
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_event_engine_cleanup():
    """Test EventEngine cleanup"""
    from src.events.engine import EventEngine
    
    print("Creating EventEngine...")
    engine = EventEngine()
    
    try:
        print("Starting EventEngine...")
        await engine.start()
        
        print("Sleeping for 0.1 seconds...")
        await asyncio.sleep(0.1)
        
        print("Stopping EventEngine...")
        await engine.stop()
        
        print("EventEngine stopped successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        await engine.stop()

async def test_agent_manager_cleanup():
    """Test AgentManager cleanup"""
    from src.agents.agent_manager import AgentManager
    from unittest.mock import AsyncMock, MagicMock
    
    print("Creating AgentManager...")
    mock_memory = AsyncMock()
    mock_llm = AsyncMock()
    mock_event_engine = MagicMock()
    
    manager = AgentManager({
        'memory_store': mock_memory,
        'default_llm_provider': mock_llm,
        'event_engine': mock_event_engine
    })
    
    try:
        print("Starting streaming...")
        await manager.start_streaming_mentions()
        
        print("Sleeping for 0.1 seconds...")
        await asyncio.sleep(0.1)
        
        print("Stopping streaming...")
        await manager.stop_streaming_mentions()
        
        print("AgentManager stopped successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        await manager.stop_streaming_mentions()

async def main():
    """Run debug tests"""
    print("=== Starting hang debug tests ===")
    
    print("\n1. Testing EventEngine cleanup...")
    await test_event_engine_cleanup()
    
    print("\n2. Testing AgentManager cleanup...")
    await test_agent_manager_cleanup()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    asyncio.run(main()) 