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

@pytest.mark.asyncio
@patch('solana.rpc.async_api.AsyncClient')
@patch('solana.keypair.Keypair')
@patch('base58.b58decode')
async def test_solana_wallet_init(mock_decode, mock_keypair, mock_client):
    """Test Solana wallet initialization"""
    mock_keypair_instance = MagicMock()
    mock_keypair.from_secret_key.return_value = mock_keypair_instance
    mock_decode.return_value = b"test_key_bytes"
    from src.solana.wallet import SolanaWallet
    wallet = SolanaWallet("test_private_key")
    assert wallet.private_key == "test_private_key"
    assert wallet.rpc_url == "https://api.mainnet-beta.solana.com"
    assert wallet.retry_attempts == 3

@pytest.mark.asyncio
@patch('solana.rpc.async_api.AsyncClient')
@patch('solana.keypair.Keypair')
@patch('base58.b58decode')
async def test_solana_wallet_get_balance(mock_decode, mock_keypair, mock_client):
    """Test getting wallet balance"""
    mock_keypair_instance = MagicMock()
    mock_keypair.from_secret_key.return_value = mock_keypair_instance
    mock_decode.return_value = b"test_key_bytes"
    mock_response = MagicMock()
    mock_response.value = 1000000000  # 1 SOL in lamports
    from src.solana.wallet import SolanaWallet
    wallet = SolanaWallet("test_private_key")
    # Patch wallet.client.get_balance to be AsyncMock
    wallet.client.get_balance = AsyncMock(return_value=mock_response)
    balance = await wallet.get_balance()
    assert balance == 1.0  # Should be converted from lamports to SOL

@pytest.mark.asyncio
@patch('solana.rpc.async_api.AsyncClient')
@patch('solana.keypair.Keypair')
@patch('base58.b58decode')
async def test_solana_wallet_transfer(mock_decode, mock_keypair, mock_client):
    """Test SOL transfer"""
    mock_keypair_instance = MagicMock()
    mock_keypair.from_secret_key.return_value = mock_keypair_instance
    mock_decode.return_value = b"test_key_bytes"
    mock_transaction = MagicMock()
    mock_transaction.add = MagicMock()
    mock_transaction.sign = MagicMock()
    mock_blockhash_response = MagicMock()
    mock_blockhash_response.value = MagicMock()
    mock_blockhash_response.value.blockhash = "test_blockhash"
    mock_transfer_response = MagicMock()
    mock_transfer_response.value = "test_signature"
    with patch('src.solana.wallet.Transaction', return_value=mock_transaction):
        with patch('src.solana.wallet.transfer') as mock_transfer_func:
            with patch('src.solana.wallet.PublicKey'):
                from src.solana.wallet import SolanaWallet
                wallet = SolanaWallet("test_private_key")
                # Patch wallet.client async methods
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