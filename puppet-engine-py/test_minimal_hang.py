#!/usr/bin/env python3
"""
Minimal test to isolate hanging issue
"""
import pytest
import asyncio

@pytest.mark.asyncio
async def test_minimal_async():
    """Minimal async test that should not hang."""
    await asyncio.sleep(0.01)
    assert True

@pytest.mark.asyncio
async def test_minimal_async_2():
    """Another minimal async test."""
    await asyncio.sleep(0.01)
    assert True

def test_minimal_sync():
    """Minimal sync test."""
    assert True 