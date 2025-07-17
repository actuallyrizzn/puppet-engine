import base58
import json
from typing import Dict, Any, Optional, List
import asyncio
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey
from ..core.models import Agent

class SolanaWallet:
    def __init__(self, private_key: str, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.private_key = private_key
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url)
        self.keypair = self._create_keypair()
        self.retry_attempts = 3
        self.retry_delay = 1.0
    
    def _create_keypair(self) -> Keypair:
        """Create keypair with multiple format support"""
        try:
            # Try base58
            decoded_key = base58.b58decode(self.private_key)
            return Keypair.from_secret_key(decoded_key)
        except Exception:
            try:
                # Try JSON array
                secret_key = bytes(json.loads(self.private_key))
                return Keypair.from_secret_key(secret_key)
            except Exception:
                try:
                    # Try hex
                    secret_key = bytes.fromhex(self.private_key)
                    return Keypair.from_secret_key(secret_key)
                except Exception as e:
                    raise Exception(f"Invalid private key format: {e}")
    
    async def get_balance(self) -> float:
        """Get wallet balance with retry logic"""
        for attempt in range(self.retry_attempts):
            try:
                response = await self.client.get_balance(self.keypair.public_key)
                if response.value is not None:
                    return response.value / 1_000_000_000  # Convert lamports to SOL
                else:
                    raise Exception("No balance data received")
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise Exception(f"Failed to get balance: {e}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        return 0.0
    
    async def transfer_sol(self, to_address: str, amount: float) -> str:
        """Transfer SOL to another address"""
        try:
            # Convert SOL to lamports
            lamports = int(amount * 1_000_000_000)
            
            # Create transfer instruction
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=self.keypair.public_key,
                    to_pubkey=PublicKey(to_address),
                    lamports=lamports
                )
            )
            
            # Create and sign transaction
            transaction = Transaction()
            transaction.add(transfer_ix)
            
            # Get recent blockhash
            blockhash_response = await self.client.get_latest_blockhash()
            if blockhash_response.value is None:
                raise Exception("Failed to get blockhash")
            
            transaction.recent_blockhash = blockhash_response.value.blockhash
            
            # Sign transaction
            transaction.sign(self.keypair)
            
            # Send transaction
            response = await self.client.send_transaction(transaction)
            if response.value is None:
                raise Exception("Failed to send transaction")
            
            return response.value
            
        except Exception as e:
            raise Exception(f"Transfer failed: {e}")
    
    async def get_token_accounts(self) -> List[Dict[str, Any]]:
        """Get all token accounts for this wallet"""
        try:
            response = await self.client.get_token_accounts_by_owner(
                self.keypair.public_key,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}
            )
            
            if response.value is None:
                return []
            
            accounts = []
            for account in response.value:
                accounts.append({
                    "pubkey": account.pubkey,
                    "account": account.account
                })
            
            return accounts
            
        except Exception as e:
            raise Exception(f"Failed to get token accounts: {e}")
    
    async def get_transaction_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transaction history"""
        try:
            response = await self.client.get_signatures_for_address(
                self.keypair.public_key,
                limit=limit
            )
            
            if response.value is None:
                return []
            
            transactions = []
            for sig in response.value:
                transactions.append({
                    "signature": sig.signature,
                    "slot": sig.slot,
                    "err": sig.err,
                    "memo": sig.memo,
                    "block_time": sig.block_time
                })
            
            return transactions
            
        except Exception as e:
            raise Exception(f"Failed to get transaction history: {e}")
    
    def get_public_key(self) -> str:
        """Get the public key as a string"""
        return str(self.keypair.public_key)
    
    async def close(self):
        """Close the RPC client"""
        await self.client.close() 