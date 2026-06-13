"""
Discord tipping bot using pydoge.

This example shows how to build a simple Discord bot that allows users
to tip each other with Dogecoin. It demonstrates:
- Async event handling with discord.py
- Integration with pydoge for wallet operations
- Error handling and user feedback
- Environment-based configuration

Requirements:
- pip install discord.py pydoge
- Set DISCORD_BOT_TOKEN environment variable
- Set DOGE_RPC_* environment variables
"""

import asyncio
import os
import re
from typing import Optional

import discord
from discord.ext import commands

from pydoge import Client, Wallet
from pydoge.exceptions import RPCError, ConnectionError


class DogeTippingBot(commands.Bot):
    """Discord bot for Dogecoin tipping."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client: Optional[Client] = None
        self.wallet: Optional[Wallet] = None

    async def setup_wallet(self):
        """Initialize the Dogecoin wallet connection."""
        rpc_url = os.getenv("DOGE_RPC_URL", "http://localhost:22555")
        rpc_user = os.getenv("DOGE_RPC_USER")
        rpc_password = os.getenv("DOGE_RPC_PASSWORD")

        if not rpc_user or not rpc_password:
            print("Warning: DOGE_RPC_USER and DOGE_RPC_PASSWORD not set")
            return

        try:
            self.client = Client(rpc_url, rpc_user, rpc_password)
            # Keep connection open for the bot's lifetime
            await self.client.__aenter__()
            self.wallet = Wallet(self.client)
            print("✅ Wallet connected successfully")
        except Exception as e:
            print(f"❌ Failed to connect wallet: {e}")

    @commands.command()
    async def balance(self, ctx):
        """Check the bot's current balance."""
        if not self.wallet:
            await ctx.send("❌ Wallet not connected. Check bot configuration.")
            return

        try:
            balance = await self.wallet.get_balance()
            await ctx.send(f"🏦 Bot balance: {balance:.8f} DOGE")
        except Exception as e:
            await ctx.send(f"❌ Error checking balance: {e}")

    @commands.command()
    async def tip(self, ctx, recipient: discord.Member, amount: float):
        """Tip Dogecoin to another user.

        Usage: !tip @user 1.5
        """
        if not self.wallet:
            await ctx.send("❌ Wallet not connected.")
            return

        if amount <= 0:
            await ctx.send("❌ Amount must be positive.")
            return

        if recipient == ctx.author:
            await ctx.send("❌ You can't tip yourself!")
            return

        try:
            # In a real implementation, you'd look up the recipient's address
            # from a database. For this example, we'll create a temporary address
            # and assume the recipient can check their wallet.
            temp_address = await self.wallet.create_address(f"tip_{recipient.id}_{ctx.message.id}")

            # Send the tip to the temporary address
            txid = await self.wallet.send(temp_address, amount, comment=f"Tip from {ctx.author}")

            await ctx.send(
                f"✅ {ctx.author.mention} tipped {recipient.mention} {amount:.8f} DOGE!\n"
                f"💰 Recipient can check their wallet for new address: `{temp_address[:16]}...`\n"
                f"📋 Transaction: `{txid[:16]}...`"
            )

        except Exception as e:
            await ctx.send(f"❌ Tip failed: {e}")

    @commands.command()
    async def address(self, ctx):
        """Get your personal Dogecoin address for receiving tips."""
        if not self.wallet:
            await ctx.send("❌ Wallet not connected.")
            return

        try:
            # Create a unique address for this user
            user_address = await self.wallet.create_address(f"user_{ctx.author.id}")
            await ctx.send(f"💰 Your Dogecoin address: `{user_address}`")
        except Exception as e:
            await ctx.send(f"❌ Error generating address: {e}")


async def main():
    """Main bot entry point."""
    # Get Discord token
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Please set DISCORD_BOT_TOKEN environment variable")
        return

    # Create bot with command prefix
    bot = DogeTippingBot(command_prefix="!", intents=discord.Intents.all())

    # Setup wallet connection
    await bot.setup_wallet()

    # Start the bot
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        print("Bot shutting down...")
    finally:
        if bot.client:
            await bot.client.__aexit__(None, None, None)


if __name__ == "__main__":
    asyncio.run(main())