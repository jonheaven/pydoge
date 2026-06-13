"""
Inscription support for pydoge.

Ported from Doginals JS implementation for Dogecoin inscriptions.
Supports both Doginals (era 1) and Dogenals (era 2) specs.
"""

import asyncio
import hashlib
import base64
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from .client import Client
from .exceptions import RPCError

# Constants from Doginals
MAX_SCRIPT_ELEMENT_SIZE = 520
MAX_CHUNK_LEN = 240
MAX_PAYLOAD_LEN = 1500

class Inscriber:
    """Handles Dogecoin inscription operations."""

    def __init__(self, client: Client, wallet_privkey: str):
        self.client = client
        self.privkey = wallet_privkey
        # TODO: Implement key handling, for now assume WIF

    async def mint(
        self,
        address: str,
        content_type_or_file: str,
        hex_data: Optional[str] = None,
        delegate_txid: Optional[str] = None
    ) -> str:
        """Mint an inscription.

        Args:
            address: Recipient address
            content_type_or_file: Content type or file path
            hex_data: Hex data if not file
            delegate_txid: For delegate inscriptions

        Returns:
            Transaction ID
        """
        # Load data
        if Path(content_type_or_file).exists():
            content_type = self._get_mime_type(content_type_or_file)
            data = Path(content_type_or_file).read_bytes()
        else:
            content_type = content_type_or_file
            data = bytes.fromhex(hex_data) if hex_data else b""

        if not data:
            raise ValueError("No data to inscribe")

        # Build inscription script (ported from JS)
        inscription_script = self._build_inscription_script(content_type, data, delegate_txid)

        # Create transactions (simplified port)
        txs = await self._create_inscription_txs(address, inscription_script)

        # Broadcast
        for tx in txs:
            await self.client._call("sendrawtransaction", tx)

        return txs[-1]['txid']  # Last tx is the reveal

    def _build_inscription_script(self, content_type: str, data: bytes, delegate_txid: Optional[str]) -> bytes:
        """Build the inscription script data."""
        # Ported from JS inscribe function
        script = b"ord"  # Marker

        if delegate_txid:
            # Delegate inscription
            script += self._number_to_bytes(1)  # Pieces
            script += self._string_to_bytes("")  # Empty content type
            script += self._number_to_bytes(0)  # Empty data
            script += self._number_to_bytes(11)  # Delegate opcode
            script += self._txid_to_bytes(delegate_txid)
        else:
            # Regular inscription
            parts = []
            while data:
                part = data[:MAX_CHUNK_LEN]
                data = data[MAX_CHUNK_LEN:]
                parts.append(part)

            script += self._number_to_bytes(len(parts))
            script += self._string_to_bytes(content_type)
            for i, part in enumerate(parts):
                script += self._number_to_bytes(len(parts) - i - 1)
                script += self._data_to_bytes(part)

        return script

    def _number_to_bytes(self, n: int) -> bytes:
        """Convert number to script bytes."""
        if n == 0:
            return b"\x00"
        elif n <= 16:
            return bytes([0x50 + n])
        elif n < 128:
            return bytes([n])
        else:
            return bytes([n % 256, n // 256])

    def _string_to_bytes(self, s: str) -> bytes:
        """Convert string to script bytes."""
        return self._data_to_bytes(s.encode('utf-8'))

    def _data_to_bytes(self, data: bytes) -> bytes:
        """Convert data to script bytes with length prefix."""
        if len(data) <= 75:
            return bytes([len(data)]) + data
        elif len(data) <= 255:
            return b"\x76" + bytes([len(data)]) + data
        else:
            return b"\x77" + bytes([len(data) % 256, len(data) // 256]) + data

    def _txid_to_bytes(self, txid: str) -> bytes:
        """Convert txid to reversed bytes."""
        return bytes.fromhex(txid)[::-1]

    async def _create_inscription_txs(self, address: str, inscription_data: bytes) -> List[Dict[str, Any]]:
        """Create the inscription transactions."""
        # Simplified: Create commit and reveal txs
        # Full implementation would build P2SH like JS
        # For now, placeholder
        commit_tx = await self._create_commit_tx(inscription_data)
        reveal_tx = await self._create_reveal_tx(address, commit_tx['txid'])
        return [commit_tx, reveal_tx]

    async def _create_commit_tx(self, data: bytes) -> Dict[str, Any]:
        """Create commit transaction."""
        # Placeholder: Use client to create tx
        # In full impl, build P2SH with inscription data
        return {"txid": "placeholder_commit"}

    async def _create_reveal_tx(self, address: str, commit_txid: str) -> Dict[str, Any]:
        """Create reveal transaction."""
        return {"txid": "placeholder_reveal"}

    async def deploy_drc20(
        self,
        address: str,
        ticker: str,
        max_supply: str,
        limit: str
    ) -> str:
        """Deploy a DRC-20 token."""
        hex_data = self._build_drc20_data("deploy", ticker, max_supply, limit)
        return await self.mint(address, "text/plain;charset=utf-8", hex_data)

    async def mint_drc20(
        self,
        address: str,
        ticker: str,
        amount: str,
        repeat: int = 1
    ) -> List[str]:
        """Mint DRC-20 tokens."""
        txids = []
        for _ in range(repeat):
            hex_data = self._build_drc20_data("mint", ticker, amount)
            txid = await self.mint(address, "text/plain;charset=utf-8", hex_data)
            txids.append(txid)
        return txids

    async def transfer_drc20(
        self,
        address: str,
        ticker: str,
        amount: str
    ) -> str:
        """Transfer DRC-20 tokens."""
        hex_data = self._build_drc20_data("transfer", ticker, amount)
        return await self.mint(address, "text/plain;charset=utf-8", hex_data)

    def _build_drc20_data(self, op: str, ticker: str, *args: str) -> str:
        """Build DRC-20 JSON data."""
        data = {
            "p": "drc-20",
            "op": op,
            "tick": ticker.lower()
        }
        if op in ["deploy", "mint", "transfer"]:
            if op == "deploy":
                data["max"] = args[0]
                data["lim"] = args[1]
            elif op == "transfer":
                data["amt"] = args[0]
        return json.dumps(data)

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type for file."""
        # Simple implementation
        ext = Path(file_path).suffix.lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.json': 'application/json'
        }
        return mime_types.get(ext, 'application/octet-stream')
