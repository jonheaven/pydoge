from unittest.mock import patch

import pytest

from pydoge.client import Client
from pydoge.exceptions import RPCError
from pydoge.models import BlockchainInfo


@pytest.mark.asyncio
async def test_getblockchaininfo():
    mock_response = {
        "chain": "main",
        "blocks": 1000,
        "headers": 1000,
        "bestblockhash": "abc123",
        "difficulty": 1.0,
        "mediantime": 1234567890,
        "verificationprogress": 1.0,
        "initialblockdownload": False,
        "chainwork": "def456",
        "size_on_disk": 1000000,
        "pruned": False,
        "softforks": [],
        "warnings": "",
    }

    with patch.object(Client, "_call", return_value=mock_response):
        client = Client("http://localhost:22555")
        info = await client.getblockchaininfo()

        assert isinstance(info, BlockchainInfo)
        assert info.chain == "main"
        assert info.blocks == 1000


@pytest.mark.asyncio
async def test_getbalance():
    with patch.object(Client, "_call", return_value="100.5"):
        client = Client("http://localhost:22555")
        balance = await client.getbalance()

        assert balance == 100.5


@pytest.mark.asyncio
async def test_rpc_error():
    with patch.object(Client, "_call", side_effect=RPCError(-1, "Test error")):
        client = Client("http://localhost:22555")

        with pytest.raises(RPCError) as exc_info:
            await client.getbalance()

        assert exc_info.value.code == -1
        assert "Test error" in exc_info.value.message
