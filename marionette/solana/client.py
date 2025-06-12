import asyncio
from typing import Dict, List, Optional, Any
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import SYS_PROGRAM_ID
from spl.token.instructions import get_associated_token_address
from ..types import Agent
from ..events.router import event_router
from ..events.handlers import EVENT_TYPES

class SolanaClient:
    """Solana client for wallet operations and token transfers."""
    
    def __init__(self, rpc_url: str):
        self.client = AsyncClient(rpc_url, commitment=Confirmed)
        self._lock = asyncio.Lock()
    
    async def connect_wallet(self, agent: Agent, keypair: Keypair) -> Dict[str, Any]:
        """Connect a wallet for an agent."""
        async with self._lock:
            try:
                # Get wallet balance
                balance = await self.client.get_balance(keypair.public_key)
                
                # Get token accounts
                token_accounts = await self.client.get_token_accounts_by_owner(
                    keypair.public_key,
                    {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}
                )
                
                # Dispatch wallet connect event
                await event_router.dispatch_event(Event(
                    type=EVENT_TYPES["WALLET_CONNECTED"],
                    agent_id=agent.id,
                    data={
                        "wallet_address": str(keypair.public_key),
                        "balance": balance["result"]["value"],
                        "token_accounts": token_accounts["result"]["value"]
                    }
                ))
                
                return {
                    "wallet_address": str(keypair.public_key),
                    "balance": balance["result"]["value"],
                    "token_accounts": token_accounts["result"]["value"]
                }
            except Exception as e:
                # Dispatch error event
                await event_router.dispatch_event(Event(
                    type=EVENT_TYPES["ERROR_OCCURRED"],
                    agent_id=agent.id,
                    data={
                        "error": str(e),
                        "operation": "wallet_connect"
                    }
                ))
                raise
    
    async def transfer_tokens(
        self,
        agent: Agent,
        from_keypair: Keypair,
        to_address: str,
        amount: int,
        token_mint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transfer SOL or SPL tokens."""
        async with self._lock:
            try:
                if token_mint:
                    # SPL token transfer
                    from_token_account = get_associated_token_address(
                        from_keypair.public_key,
                        token_mint
                    )
                    to_token_account = get_associated_token_address(
                        to_address,
                        token_mint
                    )
                    
                    # Create transfer instruction
                    transfer_ix = spl_token.transfer_checked(
                        from_token_account,
                        token_mint,
                        to_token_account,
                        from_keypair.public_key,
                        [],
                        amount,
                        9  # Default decimals
                    )
                else:
                    # SOL transfer
                    transfer_ix = system_program.transfer(
                        from_keypair.public_key,
                        to_address,
                        amount
                    )
                
                # Create and sign transaction
                transaction = Transaction().add(transfer_ix)
                result = await self.client.send_transaction(
                    transaction,
                    from_keypair,
                    opts={"skip_confirmation": False}
                )
                
                # Dispatch transfer event
                await event_router.dispatch_event(Event(
                    type=EVENT_TYPES["TOKEN_TRANSFERRED"],
                    agent_id=agent.id,
                    data={
                        "from": str(from_keypair.public_key),
                        "to": to_address,
                        "amount": amount,
                        "token_mint": token_mint,
                        "signature": result["result"]
                    }
                ))
                
                return {
                    "signature": result["result"],
                    "from": str(from_keypair.public_key),
                    "to": to_address,
                    "amount": amount,
                    "token_mint": token_mint
                }
            except Exception as e:
                # Dispatch error event
                await event_router.dispatch_event(Event(
                    type=EVENT_TYPES["ERROR_OCCURRED"],
                    agent_id=agent.id,
                    data={
                        "error": str(e),
                        "operation": "token_transfer"
                    }
                ))
                raise
    
    async def simulate_jupiter_swap(
        self,
        agent: Agent,
        from_keypair: Keypair,
        from_token: str,
        to_token: str,
        amount: int
    ) -> Dict[str, Any]:
        """Simulate a token swap using Jupiter."""
        async with self._lock:
            try:
                # Mock Jupiter API response
                # In a real implementation, this would call the Jupiter API
                mock_quote = {
                    "inputMint": from_token,
                    "outputMint": to_token,
                    "inAmount": str(amount),
                    "outAmount": str(int(amount * 0.95)),  # Mock 5% slippage
                    "priceImpactPct": 0.5,
                    "route": [
                        {
                            "protocol": "JUPITER",
                            "inAmount": str(amount),
                            "outAmount": str(int(amount * 0.95))
                        }
                    ]
                }
                
                # Dispatch swap simulation event
                await event_router.dispatch_event(Event(
                    type=EVENT_TYPES["SWAP_SIMULATED"],
                    agent_id=agent.id,
                    data={
                        "from_token": from_token,
                        "to_token": to_token,
                        "amount": amount,
                        "quote": mock_quote
                    }
                ))
                
                return mock_quote
            except Exception as e:
                # Dispatch error event
                await event_router.dispatch_event(Event(
                    type=EVENT_TYPES["ERROR_OCCURRED"],
                    agent_id=agent.id,
                    data={
                        "error": str(e),
                        "operation": "swap_simulation"
                    }
                ))
                raise
    
    async def close(self) -> None:
        """Close the Solana client connection."""
        await self.client.close() 