from unittest.mock import patch

import pytest

from pydoge.client import Client
from pydoge.exceptions import RPCError
from pydoge.wallet import Wallet


class TestWallet:
    """Test suite for Wallet class."""

    @pytest.fixture
    async def mock_wallet(self):
        """Fixture providing a mocked Wallet instance."""
        with patch.object(Client, "_call") as mock_call:
            client = Client("http://localhost:22555")
            wallet = Wallet(client)
            yield wallet, mock_call

    @pytest.mark.asyncio
    async def test_get_balance_success(self, mock_wallet):
        """Test successful get_balance call."""
        wallet, mock_call = mock_wallet
        mock_call.return_value = "100.5"

        balance = await wallet.get_balance()

        assert balance == 100.5
        mock_call.assert_called_once_with("getbalance", "*", 1)

    @pytest.mark.asyncio
    async def test_get_balance_with_params(self, mock_wallet):
        """Test get_balance with custom parameters."""
        wallet, mock_call = mock_wallet
        mock_call.return_value = "50.0"

        balance = await wallet.get_balance(minconf=6)

        assert balance == 50.0
        mock_call.assert_called_once_with("getbalance", "*", 6)

    @pytest.mark.asyncio
    async def test_get_balance_negative_minconf(self, mock_wallet):
        """Test get_balance with negative minconf raises ValueError."""
        wallet, _ = mock_wallet

        with pytest.raises(ValueError, match="minconf must be non-negative"):
            await wallet.get_balance(minconf=-1)

    @pytest.mark.asyncio
    async def test_create_address_success(self, mock_wallet):
        """Test successful create_address call."""
        wallet, mock_call = mock_wallet
        mock_call.return_value = "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

        address = await wallet.create_address("test_label")

        assert address == "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        mock_call.assert_called_once_with("getnewaddress", "test_label")

    @pytest.mark.asyncio
    async def test_create_address_no_label(self, mock_wallet):
        """Test create_address without label."""
        wallet, mock_call = mock_wallet
        mock_call.return_value = "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

        address = await wallet.create_address()

        assert address == "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        mock_call.assert_called_once_with("getnewaddress", "")

    @pytest.mark.asyncio
    async def test_send_success(self, mock_wallet):
        """Test successful send call."""
        wallet, mock_call = mock_wallet
        mock_call.return_value = "abc123def456"

        txid = await wallet.send("DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", 1.5, "comment", "to")

        assert txid == "abc123def456"
        mock_call.assert_called_once_with("sendtoaddress", "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", "1.5", "comment", "to")

    @pytest.mark.asyncio
    async def test_send_zero_amount(self, mock_wallet):
        """Test send with zero amount raises ValueError."""
        wallet, _ = mock_wallet

        with pytest.raises(ValueError, match="Amount must be positive"):
            await wallet.send("DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", 0.0)

    @pytest.mark.asyncio
    async def test_send_negative_amount(self, mock_wallet):
        """Test send with negative amount raises ValueError."""
        wallet, _ = mock_wallet

        with pytest.raises(ValueError, match="Amount must be positive"):
            await wallet.send("DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", -1.0)

    @pytest.mark.asyncio
    async def test_send_invalid_address(self, mock_wallet):
        """Test send with invalid address format raises ValueError."""
        wallet, _ = mock_wallet

        with pytest.raises(ValueError, match="Invalid Dogecoin address format"):
            await wallet.send("invalid_address", 1.0)

    @pytest.mark.asyncio
    async def test_send_short_address(self, mock_wallet):
        """Test send with too short address raises ValueError."""
        wallet, _ = mock_wallet

        with pytest.raises(ValueError, match="Invalid Dogecoin address format"):
            await wallet.send("D123", 1.0)

    @pytest.mark.asyncio
    async def test_send_wrong_prefix(self, mock_wallet):
        """Test send with wrong address prefix raises ValueError."""
        wallet, _ = mock_wallet

        with pytest.raises(ValueError, match="Invalid Dogecoin address format"):
            await wallet.send("1XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", 1.0)

    @pytest.mark.asyncio
    async def test_get_address_info_success(self, mock_wallet):
        """Test successful get_address_info call."""
        wallet, mock_call = mock_wallet
        mock_address_info = {
            "address": "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "scriptPubKey": "76a914...",
            "ismine": True,
            "iswatchonly": False,
            "isscript": False,
            "iswitness": False,
            "labels": [{"name": "test"}],
        }
        mock_call.return_value = mock_address_info

        info = await wallet.get_address_info("DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

        assert info.address == "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        assert info.ismine is True
        mock_call.assert_called_once_with("getaddressinfo", "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    @pytest.mark.asyncio
    async def test_get_address_info_invalid_address(self, mock_wallet):
        """Test get_address_info with invalid address raises ValueError."""
        wallet, _ = mock_wallet

        with pytest.raises(ValueError, match="Invalid Dogecoin address format"):
            await wallet.get_address_info("invalid")

    @pytest.mark.asyncio
    async def test_wallet_initialization(self):
        """Test wallet initialization."""
        client = Client("http://test:1234")
        wallet = Wallet(client)

        assert wallet.client is client

    @pytest.mark.asyncio
    async def test_wallet_error_propagation(self, mock_wallet):
        """Test that wallet methods propagate client errors."""
        wallet, mock_call = mock_wallet
        mock_call.side_effect = RPCError(-1, "RPC error")

        with pytest.raises(RPCError, match="RPC error"):
            await wallet.get_balance()
