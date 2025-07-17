import pytest
from unittest.mock import patch, MagicMock
import sys

# Patch sys.modules to mock solana and its submodules
sys.modules['solana'] = MagicMock()
sys.modules['solana.rpc'] = MagicMock()
sys.modules['solana.rpc.async_api'] = MagicMock()
sys.modules['solana.keypair'] = MagicMock()
sys.modules['solana.transaction'] = MagicMock()
sys.modules['solana.system_program'] = MagicMock()
sys.modules['solana.publickey'] = MagicMock()
sys.modules['base58'] = MagicMock()

from src.solana.wallet import SolanaWallet

@pytest.fixture
def wallet():
    return SolanaWallet(private_key="test_key", rpc_url="http://localhost")

def test_get_balance(wallet):
    with patch.object(wallet, 'get_balance', return_value=100):
        result = wallet.get_balance()
        assert result == 100

def test_transfer_success(wallet):
    with patch.object(wallet, 'transfer_sol', return_value={'tx': 'abc', 'status': 'success'}):
        result = wallet.transfer_sol('recipient', 1)
        assert result['status'] == 'success'

def test_transfer_error(wallet):
    with patch.object(wallet, 'transfer_sol', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            wallet.transfer_sol('recipient', 1)

def test_get_public_key(wallet):
    with patch.object(wallet, 'get_public_key', return_value='address'):
        assert wallet.get_public_key() == 'address' 