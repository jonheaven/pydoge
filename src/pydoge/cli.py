import asyncio

import typer

from .client import Client
from .wallet import Wallet

app = typer.Typer(help="Dogecoin CLI tool powered by pydoge")


@app.command()
def balance(
    rpc_url: str = typer.Option("http://localhost:22555", help="Dogecoin RPC URL"),
    rpc_user: str | None = typer.Option(None, help="RPC username"),
    rpc_password: str | None = typer.Option(None, help="RPC password"),
) -> None:
    """Get wallet balance."""

    async def _balance() -> None:
        async with Client(rpc_url, rpc_user, rpc_password) as client:
            wallet = Wallet(client)
            bal = await wallet.get_balance()
            typer.echo(f"Balance: {bal} DOGE")

    asyncio.run(_balance())


@app.command()
def send(
    address: str = typer.Argument(..., help="Recipient address"),
    amount: float = typer.Argument(..., help="Amount to send in DOGE"),
    rpc_url: str = typer.Option("http://localhost:22555", help="Dogecoin RPC URL"),
    rpc_user: str | None = typer.Option(None, help="RPC username"),
    rpc_password: str | None = typer.Option(None, help="RPC password"),
) -> None:
    """Send DOGE to an address."""

    async def _send() -> None:
        async with Client(rpc_url, rpc_user, rpc_password) as client:
            wallet = Wallet(client)
            txid = await wallet.send(address, amount)
            typer.echo(f"Sent {amount} DOGE to {address}. TXID: {txid}")

    asyncio.run(_send())


@app.command()
def new_address(
    label: str = typer.Option("", help="Address label"),
    rpc_url: str = typer.Option("http://localhost:22555", help="Dogecoin RPC URL"),
    rpc_user: str | None = typer.Option(None, help="RPC username"),
    rpc_password: str | None = typer.Option(None, help="RPC password"),
) -> None:
    """Generate a new address."""

    async def _new_address() -> None:
        async with Client(rpc_url, rpc_user, rpc_password) as client:
            wallet = Wallet(client)
            addr = await wallet.create_address(label)
            typer.echo(f"New address: {addr}")

    asyncio.run(_new_address())


def main() -> None:
    app()
