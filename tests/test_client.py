from unittest.mock import Mock, patch

import pytest

from pydoge.client import Client
from pydoge.exceptions import AuthenticationError, ConnectionError, RPCError
from pydoge.models import AddressInfo, BlockchainInfo


class TestClient:
    """Test suite for Client class."""

    @pytest.mark.asyncio
    async def test_getblockchaininfo_success(self, mock_client, mock_response):
        """Test successful getblockchaininfo call."""
        client, mock_call = mock_client
        mock_call.return_value = mock_response

        info = await client.getblockchaininfo()

        assert isinstance(info, BlockchainInfo)
        assert info.chain == "main"
        assert info.blocks == 1000
        assert info.difficulty == 1.0
        mock_call.assert_called_once_with("getblockchaininfo")

    @pytest.mark.asyncio
    async def test_getblockchaininfo_invalid_response(self, mock_client):
        """Test getblockchaininfo with invalid response type."""
        client, mock_call = mock_client
        mock_call.return_value = "invalid"

        with pytest.raises(RPCError, match="Invalid response format"):
            await client.getblockchaininfo()

    @pytest.mark.asyncio
    async def test_getbalance_success(self, mock_client):
        """Test successful getbalance call."""
        client, mock_call = mock_client
        mock_call.return_value = "100.5"

        balance = await client.getbalance()

        assert balance == 100.5
        mock_call.assert_called_once_with("getbalance", "*", 1)

    @pytest.mark.asyncio
    async def test_getbalance_with_params(self, mock_client):
        """Test getbalance with custom parameters."""
        client, mock_call = mock_client
        mock_call.return_value = "50.0"

        balance = await client.getbalance("account1", 6)

        assert balance == 50.0
        mock_call.assert_called_once_with("getbalance", "account1", 6)

    @pytest.mark.asyncio
    async def test_getbalance_invalid_format(self, mock_client):
        """Test getbalance with invalid balance format."""
        client, mock_call = mock_client
        mock_call.return_value = {"invalid": "format"}

        with pytest.raises(RPCError, match="Invalid balance format"):
            await client.getbalance()

    @pytest.mark.asyncio
    async def test_getnewaddress_success(self, mock_client):
        """Test successful getnewaddress call."""
        client, mock_call = mock_client
        mock_call.return_value = "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

        address = await client.getnewaddress("test_label")

        assert address == "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        mock_call.assert_called_once_with("getnewaddress", "test_label")

    @pytest.mark.asyncio
    async def test_getnewaddress_invalid_format(self, mock_client):
        """Test getnewaddress with invalid address format."""
        client, mock_call = mock_client
        mock_call.return_value = 12345

        with pytest.raises(RPCError, match="Invalid address format"):
            await client.getnewaddress()

    @pytest.mark.asyncio
    async def test_sendtoaddress_success(self, mock_client):
        """Test successful sendtoaddress call."""
        client, mock_call = mock_client
        mock_call.return_value = "abc123def456"

        txid = await client.sendtoaddress("DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", 1.5, "comment", "to")

        assert txid == "abc123def456"
        mock_call.assert_called_once_with("sendtoaddress", "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", "1.5", "comment", "to")

    @pytest.mark.asyncio
    async def test_sendtoaddress_invalid_txid(self, mock_client):
        """Test sendtoaddress with invalid transaction ID format."""
        client, mock_call = mock_client
        mock_call.return_value = 12345

        with pytest.raises(RPCError, match="Invalid transaction ID format"):
            await client.sendtoaddress("DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", 1.0)

    @pytest.mark.asyncio
    async def test_getaddressinfo_success(self, mock_client, mock_address_info):
        """Test successful getaddressinfo call."""
        client, mock_call = mock_client
        mock_call.return_value = mock_address_info

        info = await client.getaddressinfo("DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

        assert isinstance(info, AddressInfo)
        assert info.address == "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        assert info.ismine is True
        mock_call.assert_called_once_with("getaddressinfo", "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    @pytest.mark.asyncio
    async def test_getaddressinfo_invalid_response(self, mock_client):
        """Test getaddressinfo with invalid response type."""
        client, mock_call = mock_client
        mock_call.return_value = "invalid"

        with pytest.raises(RPCError, match="Invalid response format"):
            await client.getaddressinfo("DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    @pytest.mark.asyncio
    async def test_rpc_error_handling(self, mock_client):
        """Test RPC error handling."""
        client, mock_call = mock_client
        mock_call.side_effect = RPCError(-1, "Test error")

        with pytest.raises(RPCError) as exc_info:
            await client.getbalance()

        assert exc_info.value.code == -1
        assert "Test error" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, mock_client):
        """Test connection error handling."""
        client, mock_call = mock_client
        mock_call.side_effect = ConnectionError("Connection failed")

        with pytest.raises(ConnectionError, match="Connection failed"):
            await client.getbalance()

    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, mock_client):
        """Test authentication error handling."""
        client, mock_call = mock_client
        mock_call.side_effect = AuthenticationError("Invalid credentials")

        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            await client.getbalance()


    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test HTTP error handling."""
        client = Client("http://localhost:22555")
        with patch("httpx.AsyncClient.post") as mock_post:
            from httpx import HTTPStatusError
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": {"message": "Server error"}}
            mock_response.text = "Server error"
            mock_post.return_value = Mock(return_value=mock_response)
            mock_post.return_value.raise_for_status.side_effect = HTTPStatusError(
                "500 Server Error", request=Mock(), response=mock_response
            )

            with pytest.raises(ConnectionError, match="HTTP 500.*Server error"):
                await client.getbalance()

    @pytest.mark.asyncio
    async def test_response_id_validation(self):
        """Test response ID validation."""
        client = Client("http://localhost:22555")
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"jsonrpc": "2.0", "id": 999, "result": "100.0"}  # Wrong ID
            mock_post.return_value = Mock(return_value=mock_response)

            with pytest.raises(RPCError, match="Response ID mismatch"):
                await client.getbalance()

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization with different parameters."""
        # Basic client
        client = Client("http://test:1234")
        assert client.url == "http://test:1234"
        assert client.auth is None

        # Client with auth
        client_auth = Client("http://test:1234", "user", "pass")
        assert client_auth.auth == ("user", "pass")

        # Client with timeout
        client_timeout = Client("http://test:1234", timeout=60.0)
        assert client_timeout.timeout == 60.0
