"""
Basic wallet operations with pydoge.

This example demonstrates the core wallet functionality:
- Connecting to dogecoind
- Checking balance
- Creating addresses
- Sending transactions
"""

import asyncio
import os
from pydoge import Client, Wallet


async def main():
    # Get connection details from environment
    rpc_url = os.getenv("DOGE_RPC_URL", "http://localhost:22555")
    rpc_user = os.getenv("DOGE_RPC_USER")
    rpc_password = os.getenv("DOGE_RPC_PASSWORD")

    if not rpc_user or not rpc_password:
        print("Please set DOGE_RPC_USER and DOGE_RPC_PASSWORD environment variables")
        return

    # Connect to dogecoind
    async with Client(rpc_url, rpc_user, rpc_password) as client:
        wallet = Wallet(client)

        # Check current balance
        balance = await wallet.get_balance()
        print(f"Current balance: {balance:.8f} DOGE")

        # Create a new receiving address
        new_address = await wallet.create_address("example_address")
        print(f"New address created: {new_address}")

        # Example transaction (uncomment to actually send)
        # recipient = "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        # amount = 0.1
        # txid = await wallet.send(recipient, amount, comment="Example transaction")
        # print(f"Sent {amount} DOGE to {recipient}")
        # print(f"Transaction ID: {txid}")

        # Get blockchain info
        info = await client.getblockchaininfo()
        print(f"Current block height: {info.blocks}")
        print(f"Network: {info.chain}")


if __name__ == "__main__":
    asyncio.run(main())