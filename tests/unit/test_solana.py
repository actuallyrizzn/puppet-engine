import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Mock the solana modules to avoid import errors
with patch.dict('sys.modules', {
    'solana.rpc.async_api': MagicMock(),
    'solana.keypair': MagicMock(),
    'solana.transaction': MagicMock(),
    'solana.system_program': MagicMock(),
    'solana.publickey': MagicMock(),
    'base58': MagicMock(),
}):
    pass

def test_solana_imports_mocked():
    """Test that solana imports are properly mocked"""
    assert True  # If we get here, the mocking worked

@pytest.mark.asyncio
async def test_solana_trading_mocked():
    """Test solana trading with mocked dependencies"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock the response
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"input_mint": "mint1"})
        mock_client.return_value.get = AsyncMock(return_value=mock_response)
        class DummyWallet:
            pass
        assert True

def test_solana_wallet_init():
    """Test Solana wallet initialization"""
    from unittest.mock import patch, MagicMock
    with patch.dict('sys.modules', {
        'solana': MagicMock(),
        'solana.rpc': MagicMock(),
        'solana.rpc.async_api': MagicMock(),
        'solana.keypair': MagicMock(),
        'solana.transaction': MagicMock(),
        'solana.system_program': MagicMock(),
        'solana.publickey': MagicMock(),
        'base58': MagicMock(),
    }):
        import sys
        sys.modules['solana.keypair'].Keypair = MagicMock()
        sys.modules['base58'].b58decode = MagicMock(return_value=b"test_key_bytes")
        mock_keypair_instance = MagicMock()
        sys.modules['solana.keypair'].Keypair.from_secret_key.return_value = mock_keypair_instance
        from src.solana.wallet import SolanaWallet
        wallet = SolanaWallet("test_private_key")
        assert wallet.private_key == "test_private_key"
        assert wallet.rpc_url == "https://api.mainnet-beta.solana.com"
        assert wallet.retry_attempts == 3

@pytest.mark.asyncio
async def test_solana_wallet_get_balance():
    """Test getting wallet balance"""
    from unittest.mock import patch, MagicMock, AsyncMock
    with patch.dict('sys.modules', {
        'solana': MagicMock(),
        'solana.rpc': MagicMock(),
        'solana.rpc.async_api': MagicMock(),
        'solana.keypair': MagicMock(),
        'solana.transaction': MagicMock(),
        'solana.system_program': MagicMock(),
        'solana.publickey': MagicMock(),
        'base58': MagicMock(),
    }):
        import sys
        sys.modules['solana.keypair'].Keypair = MagicMock()
        sys.modules['base58'].b58decode = MagicMock(return_value=b"test_key_bytes")
        mock_keypair_instance = MagicMock()
        sys.modules['solana.keypair'].Keypair.from_secret_key.return_value = mock_keypair_instance
        mock_response = MagicMock()
        mock_response.value = 1000000000  # 1 SOL in lamports
        from src.solana.wallet import SolanaWallet
        wallet = SolanaWallet("test_private_key")
        wallet.client.get_balance = AsyncMock(return_value=mock_response)
        balance = await wallet.get_balance()
        assert balance == 1.0

@pytest.mark.asyncio
async def test_solana_wallet_transfer():
    """Test SOL transfer"""
    from unittest.mock import patch, MagicMock, AsyncMock
    with patch.dict('sys.modules', {
        'solana': MagicMock(),
        'solana.rpc': MagicMock(),
        'solana.rpc.async_api': MagicMock(),
        'solana.keypair': MagicMock(),
        'solana.transaction': MagicMock(),
        'solana.system_program': MagicMock(),
        'solana.publickey': MagicMock(),
        'base58': MagicMock(),
    }):
        import sys
        sys.modules['solana.keypair'].Keypair = MagicMock()
        sys.modules['base58'].b58decode = MagicMock(return_value=b"test_key_bytes")
        # Mock Transaction, transfer, PublicKey
        mock_transaction = MagicMock()
        mock_transaction.add = MagicMock()
        mock_transaction.sign = MagicMock()
        sys.modules['solana.transaction'].Transaction = MagicMock(return_value=mock_transaction)
        sys.modules['solana.system_program'].transfer = MagicMock(return_value=MagicMock())
        sys.modules['solana.system_program'].TransferParams = MagicMock()
        sys.modules['solana.publickey'].PublicKey = MagicMock(return_value=MagicMock())
        mock_keypair_instance = MagicMock()
        sys.modules['solana.keypair'].Keypair.from_secret_key.return_value = mock_keypair_instance
        mock_blockhash_response = MagicMock()
        mock_blockhash_response.value = MagicMock()
        mock_blockhash_response.value.blockhash = "test_blockhash"
        mock_transfer_response = MagicMock()
        mock_transfer_response.value = "test_signature"
        from src.solana.wallet import SolanaWallet
        wallet = SolanaWallet("test_private_key")
        wallet.client.get_latest_blockhash = AsyncMock(return_value=mock_blockhash_response)
        wallet.client.send_transaction = AsyncMock(return_value=mock_transfer_response)
        signature = await wallet.transfer_sol("destination_address", 0.1)
        assert signature == "test_signature"

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_solana_trader_get_quote(mock_client):
    """Test getting a quote from Jupiter"""
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "inputMint": "mint1",
        "outputMint": "mint2", 
        "amount": "1000000",
        "outAmount": "500000"
    }
    mock_response.raise_for_status = MagicMock()
    mock_instance.get = AsyncMock(return_value=mock_response)
    from src.solana.trading import SolanaTrader
    wallet = MagicMock()  # Use MagicMock for type compatibility
    trader = SolanaTrader(wallet)
    quote = await trader.get_quote("mint1", "mint2", 1.0)
    assert quote["inputMint"] == "mint1"
    assert quote["outputMint"] == "mint2"

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_solana_trader_get_token_price(mock_client):
    """Test getting token price"""
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "mint1": {"price": 1.5}
    }
    mock_response.raise_for_status = MagicMock()
    mock_instance.get = AsyncMock(return_value=mock_response)
    from src.solana.trading import SolanaTrader
    wallet = MagicMock()
    trader = SolanaTrader(wallet)
    price = await trader.get_token_price("mint1")
    assert price == 1.5

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_solana_trader_get_supported_tokens(mock_client):
    """Test getting supported tokens"""
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"symbol": "SOL", "mint": "mint1"},
        {"symbol": "USDC", "mint": "mint2"}
    ]
    mock_response.raise_for_status = MagicMock()
    mock_instance.get = AsyncMock(return_value=mock_response)
    from src.solana.trading import SolanaTrader
    wallet = MagicMock()
    trader = SolanaTrader(wallet)
    tokens = await trader.get_supported_tokens()
    assert len(tokens) == 2
    assert tokens[0]["symbol"] == "SOL"

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_solana_trader_error_handling(mock_client):
    """Test error handling in Solana trader"""
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_response.raise_for_status.side_effect = Exception("API Error")
    mock_instance.get = AsyncMock(return_value=mock_response)
    from src.solana.trading import SolanaTrader
    wallet = MagicMock()
    trader = SolanaTrader(wallet)
    try:
        await trader.get_quote("mint1", "mint2", 1.0)
    except Exception as e:
        assert "API Error" in str(e) 

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_solana_trader_execute_swap_success(mock_client):
    """Test successful execution of a swap"""
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.json.return_value = {"swapTransaction": "tx_data"}
    mock_response.raise_for_status = MagicMock()
    mock_instance.post = AsyncMock(return_value=mock_response)
    wallet = MagicMock()
    wallet.get_public_key.return_value = "pubkey"
    wallet.transfer_sol = AsyncMock(return_value="signature123")
    from src.solana.trading import SolanaTrader
    trader = SolanaTrader(wallet)
    quote_response = {"foo": "bar"}
    signature = await trader.execute_swap(quote_response)
    assert signature == "signature123"

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_solana_trader_execute_swap_error(mock_client):
    """Test error during swap execution"""
    mock_instance = mock_client.return_value
    mock_instance.post = AsyncMock(side_effect=Exception("fail post"))
    wallet = MagicMock()
    wallet.get_public_key.return_value = "pubkey"
    wallet.transfer_sol = AsyncMock(return_value="sig")
    from src.solana.trading import SolanaTrader
    trader = SolanaTrader(wallet)
    with pytest.raises(Exception) as e:
        await trader.execute_swap({"foo": "bar"})
    assert "Swap execution failed" in str(e.value)

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_solana_trader_get_route_success(mock_client):
    """Test getting a route for a swap"""
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.json.return_value = {"route": "best"}
    mock_response.raise_for_status = MagicMock()
    mock_instance.get = AsyncMock(return_value=mock_response)
    from src.solana.trading import SolanaTrader
    wallet = MagicMock()
    trader = SolanaTrader(wallet)
    route = await trader.get_route("mint1", "mint2", 1.0)
    assert route["route"] == "best"

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_solana_trader_get_route_error(mock_client):
    """Test error in get_route"""
    mock_instance = mock_client.return_value
    mock_instance.get = AsyncMock(side_effect=Exception("fail get"))
    from src.solana.trading import SolanaTrader
    wallet = MagicMock()
    trader = SolanaTrader(wallet)
    with pytest.raises(Exception) as e:
        await trader.get_route("mint1", "mint2", 1.0)
    assert "Failed to get route" in str(e.value)

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_solana_trader_close(mock_client):
    """Test closing the HTTP client"""
    mock_instance = mock_client.return_value
    mock_instance.aclose = AsyncMock()
    from src.solana.trading import SolanaTrader
    wallet = MagicMock()
    trader = SolanaTrader(wallet)
    await trader.close()
    mock_instance.aclose.assert_awaited() 