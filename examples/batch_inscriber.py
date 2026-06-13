#!/usr/bin/env python3
"""
Batch Inscriber Example for pydoge

Poached and adapted from martinseeger2002-dogcoin_ordinal_auto_inscriber
Demonstrates batch inscription minting with confirmation waiting.
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any

from pydoge import Client, Inscriber


async def load_airdrop_list(json_file: str) -> List[Dict[str, Any]]:
    """Load airdrop list from JSON file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('airDropList', [])


async def wait_for_confirmation(txid: str, client: Client, max_retries: int = 500) -> bool:
    """Wait for transaction confirmation."""
    for attempt in range(max_retries):
        try:
            # Check transaction details
            tx_info = await client._call("gettransaction", txid)
            if tx_info and tx_info.get("confirmations", 0) >= 1:
                print(f"Transaction {txid} confirmed!")
                return True
        except Exception as e:
            print(f"Error checking confirmation for {txid}: {e}")

        if attempt < max_retries - 1:
            print(f"Waiting for confirmation... (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(10)  # Wait 10 seconds

    print(f"Failed to confirm transaction {txid} after {max_retries} attempts")
    return False


async def batch_mint_inscriptions(
    client: Client,
    inscriber: Inscriber,
    airdrop_list: List[Dict[str, Any]],
    start_index: int = 0,
    batch_size: int = 12
) -> List[str]:
    """Batch mint inscriptions with confirmation waiting."""
    successful_txids = []

    for batch_start in range(start_index, len(airdrop_list), batch_size):
        batch_end = min(batch_start + batch_size, len(airdrop_list))
        print(f"Processing batch {batch_start + 1}-{batch_end} of {len(airdrop_list)}")

        batch_txids = []

        # Mint each inscription in the batch
        for i in range(batch_start, batch_end):
            if i >= len(airdrop_list):
                break

            entry = airdrop_list[i]
            address = entry['address']

            # Create a simple text inscription for this example
            content = f"Inscription #{i + 1} for {address}"
            hex_data = content.encode().hex()

            try:
                txid = await inscriber.mint(address, "text/plain", hex_data)
                print(f"Minted inscription {i + 1}: {txid}")
                batch_txids.append(txid)
            except Exception as e:
                print(f"Failed to mint inscription {i + 1}: {e}")
                continue

        # Wait for the last transaction in the batch to confirm
        if batch_txids:
            last_txid = batch_txids[-1]
            print(f"Waiting for batch confirmation (last TXID: {last_txid})")
            if await wait_for_confirmation(last_txid, client):
                successful_txids.extend(batch_txids)
            else:
                print("Batch confirmation failed, but continuing...")

    return successful_txids


async def main():
    """Main batch inscribing function."""
    # Configuration
    RPC_URL = os.getenv("DOGE_RPC_URL", "http://localhost:22555")
    RPC_USER = os.getenv("DOGE_RPC_USER", "your_user")
    RPC_PASS = os.getenv("DOGE_RPC_PASS", "your_pass")
    WALLET_PRIVKEY = os.getenv("WALLET_PRIVKEY", "your_wif_private_key")

    # Load airdrop list
    airdrop_file = "airDropList.json"
    if not Path(airdrop_file).exists():
        print(f"Airdrop file {airdrop_file} not found. Creating sample...")
        sample_list = [
            {"address": "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
            {"address": "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
        ]
        with open(airdrop_file, 'w') as f:
            json.dump({"airDropList": sample_list}, f, indent=2)
        print("Created sample airdrop list. Edit it with your addresses.")

    airdrop_list = await load_airdrop_list(airdrop_file)
    print(f"Loaded {len(airdrop_list)} addresses for batch minting")

    # Setup client and inscriber
    async with Client(RPC_URL, RPC_USER, RPC_PASS) as client:
        inscriber = Inscriber(client, WALLET_PRIVKEY)

        # Perform batch minting
        successful_txids = await batch_mint_inscriptions(client, inscriber, airdrop_list)

        print(f"\nBatch minting complete!")
        print(f"Successfully minted {len(successful_txids)} inscriptions")
        print("Transaction IDs:")
        for txid in successful_txids:
            print(f"  {txid}")


if __name__ == "__main__":
    asyncio.run(main())