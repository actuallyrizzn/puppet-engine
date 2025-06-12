import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from solana.keypair import Keypair
from ..solana.client import SolanaClient
from ..types import Agent, Event
from ..events.handlers import EVENT_TYPES

@pytest.fixture
def mock_solana_client():
    """Mock Solana RPC client for testing."""
    with patch("solana.rpc.async_api.AsyncClient") as mock:
        mock_client = AsyncMock()
        mock.return_value = mock_client
        
        # Mock get_balance response
        mock_client.get_balance.return_value = {
            "result": {"value": 1000000000}  # 1 SOL
        }
        
        # Mock get_token_accounts response
        mock_client.get_token_accounts_by_owner.return_value = {
            "result": {
                "value": [
                    {
                        "pubkey": "token_account_1",
                        "account": {
                            "data": {
                                "parsed": {
                                    "info": {
                                        "mint": "token_mint_1",
                                        "amount": "1000000"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        # Mock send_transaction response
        mock_client.send_transaction.return_value = {
            "result": "transaction_signature"
        }
        
        yield mock_client

@pytest.fixture
def mock_event_router():
    """Mock event router for testing."""
    with patch("marionette.events.router.event_router") as mock:
        mock.dispatch_event = AsyncMock()
        yield mock

@pytest.fixture
def test_agent():
    """Create a test agent."""
    return Agent(
        id="test-agent-1",
        name="Test Agent",
        personality={
            "name": "Test Personality",
            "description": "A test personality",
            "traits": ["friendly", "curious"]
        },
        style_guide={
            "tone": "casual",
            "language": "english",
            "quirks": ["uses emojis", "talks in third person"]
        }
    )

@pytest.fixture
def test_keypair():
    """Create a test keypair."""
    return Keypair()

@pytest.fixture
def solana_client(mock_solana_client, mock_event_router):
    """Create a Solana client instance."""
    return SolanaClient("https://api.testnet.solana.com")

@pytest.mark.asyncio
async def test_connect_wallet(solana_client, test_agent, test_keypair, mock_solana_client, mock_event_router):
    """Test connecting a wallet."""
    result = await solana_client.connect_wallet(test_agent, test_keypair)
    
    assert result["wallet_address"] == str(test_keypair.public_key)
    assert result["balance"] == 1000000000
    assert len(result["token_accounts"]) == 1
    
    # Check event dispatch
    mock_event_router.dispatch_event.assert_called_once()
    event = mock_event_router.dispatch_event.call_args[0][0]
    assert event.type == EVENT_TYPES["WALLET_CONNECTED"]
    assert event.agent_id == test_agent.id
    assert event.data["wallet_address"] == str(test_keypair.public_key)

@pytest.mark.asyncio
async def test_transfer_sol(solana_client, test_agent, test_keypair, mock_solana_client, mock_event_router):
    """Test transferring SOL."""
    result = await solana_client.transfer_tokens(
        test_agent,
        test_keypair,
        "destination_address",
        100000000  # 0.1 SOL
    )
    
    assert result["signature"] == "transaction_signature"
    assert result["from"] == str(test_keypair.public_key)
    assert result["to"] == "destination_address"
    assert result["amount"] == 100000000
    assert result["token_mint"] is None
    
    # Check event dispatch
    mock_event_router.dispatch_event.assert_called_once()
    event = mock_event_router.dispatch_event.call_args[0][0]
    assert event.type == EVENT_TYPES["TOKEN_TRANSFERRED"]
    assert event.agent_id == test_agent.id
    assert event.data["from"] == str(test_keypair.public_key)

@pytest.mark.asyncio
async def test_transfer_spl_token(solana_client, test_agent, test_keypair, mock_solana_client, mock_event_router):
    """Test transferring SPL tokens."""
    result = await solana_client.transfer_tokens(
        test_agent,
        test_keypair,
        "destination_address",
        1000000,
        "token_mint_address"
    )
    
    assert result["signature"] == "transaction_signature"
    assert result["from"] == str(test_keypair.public_key)
    assert result["to"] == "destination_address"
    assert result["amount"] == 1000000
    assert result["token_mint"] == "token_mint_address"
    
    # Check event dispatch
    mock_event_router.dispatch_event.assert_called_once()
    event = mock_event_router.dispatch_event.call_args[0][0]
    assert event.type == EVENT_TYPES["TOKEN_TRANSFERRED"]
    assert event.agent_id == test_agent.id
    assert event.data["token_mint"] == "token_mint_address"

@pytest.mark.asyncio
async def test_simulate_jupiter_swap(solana_client, test_agent, test_keypair, mock_event_router):
    """Test simulating a Jupiter swap."""
    result = await solana_client.simulate_jupiter_swap(
        test_agent,
        test_keypair,
        "from_token_mint",
        "to_token_mint",
        1000000
    )
    
    assert result["inputMint"] == "from_token_mint"
    assert result["outputMint"] == "to_token_mint"
    assert result["inAmount"] == "1000000"
    assert result["outAmount"] == "950000"  # 5% slippage
    assert result["priceImpactPct"] == 0.5
    
    # Check event dispatch
    mock_event_router.dispatch_event.assert_called_once()
    event = mock_event_router.dispatch_event.call_args[0][0]
    assert event.type == EVENT_TYPES["SWAP_SIMULATED"]
    assert event.agent_id == test_agent.id
    assert event.data["from_token"] == "from_token_mint"
    assert event.data["to_token"] == "to_token_mint"

@pytest.mark.asyncio
async def test_error_handling(solana_client, test_agent, test_keypair, mock_solana_client, mock_event_router):
    """Test error handling."""
    # Mock RPC error
    mock_solana_client.get_balance.side_effect = Exception("RPC error")
    
    with pytest.raises(Exception) as exc_info:
        await solana_client.connect_wallet(test_agent, test_keypair)
    
    assert "RPC error" in str(exc_info.value)
    
    # Check error event dispatch
    mock_event_router.dispatch_event.assert_called_once()
    event = mock_event_router.dispatch_event.call_args[0][0]
    assert event.type == EVENT_TYPES["ERROR_OCCURRED"]
    assert event.agent_id == test_agent.id
    assert event.data["error"] == "RPC error"
    assert event.data["operation"] == "wallet_connect" 