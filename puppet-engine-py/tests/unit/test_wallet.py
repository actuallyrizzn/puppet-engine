import pytest
from unittest.mock import patch, MagicMock
from src.solana.wallet import SolanaWallet

@pytest.fixture
def wallet():
    return SolanaWallet(keypair=MagicMock(), rpc_url='http://localhost')

def test_get_balance(wallet):
    with patch.object(wallet, 'fetch_balance', return_value=100):
        result = wallet.get_balance()
        assert result == 100

def test_transfer_success(wallet):
    with patch.object(wallet, 'transfer', return_value={'tx': 'abc', 'status': 'success'}):
        result = wallet.transfer('recipient', 1)
        assert result['status'] == 'success'

def test_transfer_error(wallet):
    with patch.object(wallet, 'transfer', side_effect=Exception('fail')):
        with pytest.raises(Exception):
            wallet.transfer('recipient', 1)

def test_get_address(wallet):
    with patch.object(wallet, 'get_address', return_value='address'):
        assert wallet.get_address() == 'address' 