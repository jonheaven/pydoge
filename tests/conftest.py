from unittest.mock import patch

import pytest

from pydoge.client import Client


@pytest.fixture
async def mock_client():
    """Fixture providing a mocked Client instance."""
    with patch.object(Client, "_call") as mock_call:
        client = Client("http://localhost:22555")
        yield client, mock_call


@pytest.fixture
def mock_response():
    """Fixture providing a sample blockchain info response."""
    return {
        "chain": "main",
        "blocks": 1000,
        "headers": 1000,
        "bestblockhash": "a" * 64,
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


@pytest.fixture
def mock_address_info():
    """Fixture providing a sample address info response."""
    return {
        "address": "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "scriptPubKey": "76a914...",
        "ismine": True,
        "iswatchonly": False,
        "isscript": False,
        "iswitness": False,
        "labels": [{"name": "test"}],
    }
