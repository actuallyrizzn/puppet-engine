import httpx
from typing import Dict, Any, Optional, List
from .wallet import SolanaWallet

class SolanaTrader:
    def __init__(self, wallet: SolanaWallet):
        self.wallet = wallet
        self.client = httpx.AsyncClient(timeout=30.0)
        self.jupiter_api_url = "https://quote-api.jup.ag/v6"
    
    async def get_quote(self, input_mint: str, output_mint: str, amount: float) -> Dict[str, Any]:
        """Get a quote for swapping tokens via Jupiter"""
        url = f"{self.jupiter_api_url}/quote"
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(int(amount)),
            "slippageBps": "50"  # 0.5% slippage
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"Jupiter API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Failed to get quote: {e}")
    
    async def execute_swap(self, quote_response: Dict[str, Any]) -> str:
        """Execute a token swap using Jupiter"""
        try:
            # Get swap transaction
            swap_url = f"{self.jupiter_api_url}/swap"
            swap_data = {
                "quoteResponse": quote_response,
                "userPublicKey": self.wallet.get_public_key(),
                "wrapUnwrapSOL": True
            }
            
            response = await self.client.post(swap_url, json=swap_data)
            response.raise_for_status()
            swap_result = response.json()
            
            # Execute the transaction
            transaction_signature = await self.wallet.transfer_sol(
                swap_result["swapTransaction"],
                0.001  # Small amount for transaction fee
            )
            
            return transaction_signature
            
        except Exception as e:
            raise Exception(f"Swap execution failed: {e}")
    
    async def get_token_price(self, token_mint: str) -> float:
        """Get token price in USD via Jupiter price API"""
        url = f"{self.jupiter_api_url}/price"
        params = {"ids": token_mint}
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if token_mint in data and "price" in data[token_mint]:
                return data[token_mint]["price"]
            else:
                raise Exception("Price not found for token")
                
        except httpx.HTTPStatusError as e:
            raise Exception(f"Price API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Failed to get token price: {e}")
    
    async def get_supported_tokens(self) -> List[Dict[str, Any]]:
        """Get list of supported tokens for trading"""
        url = f"{self.jupiter_api_url}/tokens"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"Tokens API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Failed to get supported tokens: {e}")
    
    async def get_route(self, input_mint: str, output_mint: str, amount: float) -> Dict[str, Any]:
        """Get the best route for a swap"""
        url = f"{self.jupiter_api_url}/quote"
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(int(amount)),
            "slippageBps": "50",
            "onlyDirectRoutes": False
        }
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"Route API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Failed to get route: {e}")
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose() 