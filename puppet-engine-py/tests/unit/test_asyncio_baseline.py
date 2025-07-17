import pytest
import asyncio

@pytest.mark.asyncio
def test_asyncio_baseline():
    async def inner():
        await asyncio.sleep(0.1)
        assert True
    asyncio.run(inner()) 