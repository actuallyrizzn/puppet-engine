from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
import base58
from typing import Dict, Any, Optional
import asyncio

class SolanaWallet:
    def __init__(self, private_key: str, rpc_url: str):
        self.private_key = private_key
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url)
        self.keypair = self._create_keypair()
        self.retry_attempts = 3
    
    def _create_keypair(self) -> Keypair:
        try:
            # Try base58
            decoded_key = base58.b58decode(self.private_key)
            return Keypair.from_secret_key(decoded_key)
        except Exception:
            try:
                # Try JSON array
                import json
                secret_key = bytes(json.loads(self.private_key))
                return Keypair.from_secret_key(secret_key)
            except Exception:
                # Try hex
                secret_key = bytes.fromhex(self.private_key)
                return Keypair.from_secret_key(secret_key)
    
    async def get_balance(self) -> float:
        for attempt in range(self.retry_attempts):
            try:
                response = await self.client.get_balance(self.keypair.public_key)
                return response.value / 1_000_000_000  # Convert lamports to SOL
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise Exception(f"Failed to get balance: {e}")
                await asyncio.sleep(2 ** attempt)
        return 0.0  # Fallback return
    
    async def transfer_sol(self, to_address: str, amount: float) -> str:
        to_pubkey = PublicKey(to_address)
        transfer_ix = transfer(
            TransferParams(
                from_pubkey=self.keypair.public_key,
                to_pubkey=to_pubkey,
                lamports=int(amount * 1_000_000_000)  # Convert SOL to lamports
            )
        )
        
        transaction = Transaction().add(transfer_ix)
        
        for attempt in range(self.retry_attempts):
            try:
                result = await self.client.send_transaction(transaction, self.keypair)
                return result.value
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise Exception(f"Transfer failed: {e}")
                await asyncio.sleep(2 ** attempt)
        return ""  # Fallback return
    
    async def get_token_accounts(self) -> Dict[str, Any]:
        try:
            response = await self.client.get_token_accounts_by_owner(
                self.keypair.public_key,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}
            )
            return response.value
        except Exception as e:
            raise Exception(f"Failed to get token accounts: {e}")
    
    async def close(self):
        await self.client.close() 