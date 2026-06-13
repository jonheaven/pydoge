"""
Doginals v1 helpers for pydoge.

Provides era 1 Doginals protocol support for backwards compatibility.
Doginals v1 uses "ord" protocol identifier and focuses on basic inscriptions.
"""

import json
from typing import Dict, Any, Optional
from .inscriptions import Inscriber
from .client import Client


class DoginalsHelper:
    """Helpers for Doginals era 1 features."""

    def __init__(self, inscriber: Inscriber, client: Client):
        self.inscriber = inscriber
        self.client = client

    async def inscribe_text(self, address: str, text: str) -> str:
        """Inscribe plain text content."""
        return await self.inscriber.mint(address, "text/plain;charset=utf-8", text.encode().hex())

    async def inscribe_file(self, address: str, file_path: str) -> str:
        """Inscribe a file."""
        return await self.inscriber.mint(address, file_path, file_path)

    async def inscribe_json(self, address: str, data: Dict[str, Any]) -> str:
        """Inscribe JSON metadata."""
        json_str = json.dumps(data, separators=(',', ':'))
        return await self.inscriber.mint(address, "application/json", json_str.encode().hex())

    async def create_delegate_inscription(self, address: str, delegate_txid: str) -> str:
        """Create a delegate inscription that references another."""
        return await self.inscriber.mint(address, "text/plain", "", delegate_txid)

    async def inscribe_parent_child(
        self,
        parent_address: str,
        child_address: str,
        parent_content: str,
        child_content: str
    ) -> Dict[str, str]:
        """Create parent-child inscription relationship."""
        # Inscribe parent first
        parent_txid = await self.inscribe_text(parent_address, parent_content)

        # Create child with parent reference (using metaprotocol)
        child_data = {
            "p": "doginals",
            "op": "child",
            "parent": parent_txid
        }
        child_txid = await self.inscribe_json(child_address, child_data)

        return {
            "parent_txid": parent_txid,
            "child_txid": child_txid
        }

    async def inscribe_collection_item(
        self,
        address: str,
        collection_name: str,
        item_name: str,
        attributes: Dict[str, Any]
    ) -> str:
        """Inscribe a collection item with metadata."""
        data = {
            "p": "doginals",
            "op": "collection-item",
            "collection": collection_name,
            "name": item_name,
            "attributes": attributes
        }
        return await self.inscribe_json(address, data)

    async def create_cursed_inscription(
        self,
        address: str,
        content: str,
        curse_reason: str
    ) -> str:
        """Create a cursed inscription (reinscription of existing sat)."""
        # Note: This is a conceptual implementation
        # Actual cursed inscriptions require specific satoshi selection
        data = {
            "p": "doginals",
            "op": "curse",
            "reason": curse_reason,
            "content": content
        }
        return await self.inscribe_json(address, data)