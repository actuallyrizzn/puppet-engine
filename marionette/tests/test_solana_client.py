import pytest
from marionette.solana.solana_client import SolanaClient

@pytest.mark.asyncio
async def test_wallet_connect_test():
    client = SolanaClient()
    pubkey = await client.wallet_connect_test()
    assert isinstance(pubkey, str)
    assert len(pubkey) > 0

@pytest.mark.asyncio
async def test_stub_token_transfer():
    client = SolanaClient()
    result = await client.stub_token_transfer("from_pub", "to_pub", 1.23)
    assert "Simulated transfer" in result

@pytest.mark.asyncio
async def test_mock_jupiter_swap():
    client = SolanaClient()
    result = await client.mock_jupiter_swap("SOL", "USDC", 5.0)
    assert "Mock swap" in result 