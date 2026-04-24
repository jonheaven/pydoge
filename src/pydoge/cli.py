import asyncio
import os
from typing import Annotated

import typer

from .client import Client
from .exceptions import AuthenticationError, ConnectionError, RPCError
from .wallet import Wallet

app = typer.Typer(
    help="Dogecoin CLI tool powered by pydoge",
    add_completion=True,
    rich_markup_mode="rich",
)


def get_default_url() -> str:
    """Get default RPC URL from environment or fallback."""
    return os.getenv("DOGE_RPC_URL", "http://localhost:22555")


def get_default_user() -> str | None:
    """Get default RPC user from environment."""
    return os.getenv("DOGE_RPC_USER")


def get_default_password() -> str | None:
    """Get default RPC password from environment."""
    return os.getenv("DOGE_RPC_PASSWORD")


async def create_client(
    url: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> Client:
    """Create and return a configured Client instance."""
    rpc_url = url or get_default_url()
    rpc_user = user if user is not None else get_default_user()
    rpc_password = password if password is not None else get_default_password()

    return Client(rpc_url, rpc_user, rpc_password)


async def handle_wallet_command(
    command: str,
    *args: str,
    url: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> None:
    """Handle wallet commands with proper error handling."""
    try:
        async with await create_client(url, user, password) as client:
            wallet = Wallet(client)
            result = await getattr(wallet, command)(*args)
            typer.echo(result)
    except ValueError as e:
        typer.echo(f"❌ Input validation error: {e}", err=True)
        raise typer.Exit(1) from None
    except AuthenticationError as e:
        typer.echo(f"❌ Authentication failed: {e}", err=True)
        raise typer.Exit(1) from None
    except ConnectionError as e:
        typer.echo(f"❌ Connection error: {e}", err=True)
        raise typer.Exit(1) from None
    except RPCError as e:
        typer.echo(f"❌ RPC error: {e}", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1) from None


@app.command()
def balance(
    rpc_url: Annotated[
        str | None,
        typer.Option(
            help="Dogecoin RPC URL",
            envvar="DOGE_RPC_URL",
        ),
    ] = None,
    rpc_user: Annotated[
        str | None,
        typer.Option(
            help="RPC username",
            envvar="DOGE_RPC_USER",
        ),
    ] = None,
    rpc_password: Annotated[
        str | None,
        typer.Option(
            help="RPC password",
            envvar="DOGE_RPC_PASSWORD",
        ),
    ] = None,
    minconf: Annotated[
        int,
        typer.Option(
            help="Minimum confirmations required",
            min=0,
        ),
    ] = 1,
) -> None:
    """Get wallet balance.

    Shows the total confirmed balance in your Dogecoin wallet.

    Example:
        pydoge balance
        pydoge balance --minconf 6
    """

    async def _balance() -> None:
        try:
            async with await create_client(rpc_url, rpc_user, rpc_password) as client:
                wallet = Wallet(client)
                bal = await wallet.get_balance(minconf=minconf)
                typer.echo(f"Balance: {bal:.8f} DOGE")
        except ValueError as e:
            typer.echo(f"❌ Invalid parameters: {e}", err=True)
            raise typer.Exit(1) from None
        except AuthenticationError as e:
            typer.echo(f"❌ Authentication failed: {e}", err=True)
            typer.echo("💡 Check your DOGE_RPC_USER and DOGE_RPC_PASSWORD", err=True)
            raise typer.Exit(1) from None
        except ConnectionError as e:
            typer.echo(f"❌ Connection error: {e}", err=True)
            typer.echo("💡 Make sure dogecoind is running and accessible", err=True)
            raise typer.Exit(1) from None
        except RPCError as e:
            typer.echo(f"❌ RPC error: {e}", err=True)
            raise typer.Exit(1) from None
        except Exception as e:
            typer.echo(f"❌ Unexpected error: {e}", err=True)
            raise typer.Exit(1) from None

    asyncio.run(_balance())


@app.command()
def send(
    address: Annotated[
        str,
        typer.Argument(help="Recipient Dogecoin address (must start with 'D')"),
    ],
    amount: Annotated[
        float,
        typer.Argument(help="Amount to send in DOGE", min=0.00000001),
    ],
    comment: Annotated[
        str,
        typer.Option(help="Transaction comment"),
    ] = "",
    comment_to: Annotated[
        str,
        typer.Option(help="Comment for recipient"),
    ] = "",
    rpc_url: Annotated[
        str | None,
        typer.Option(
            help="Dogecoin RPC URL",
            envvar="DOGE_RPC_URL",
        ),
    ] = None,
    rpc_user: Annotated[
        str | None,
        typer.Option(
            help="RPC username",
            envvar="DOGE_RPC_USER",
        ),
    ] = None,
    rpc_password: Annotated[
        str | None,
        typer.Option(
            help="RPC password",
            envvar="DOGE_RPC_PASSWORD",
        ),
    ] = None,
) -> None:
    """Send Dogecoin to an address.

    Transfers the specified amount to the given address.

    Example:
        pydoge send DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX 1.5 --comment "Thanks!"
    """

    async def _send() -> None:
        try:
            async with await create_client(rpc_url, rpc_user, rpc_password) as client:
                wallet = Wallet(client)
                txid = await wallet.send(address, amount, comment, comment_to)
                typer.echo(f"✅ Sent {amount} DOGE to {address}")
                typer.echo(f"📋 Transaction ID: {txid}")
        except ValueError as e:
            typer.echo(f"❌ Invalid input: {e}", err=True)
            typer.echo("💡 Address must start with 'D' and be 26-35 characters", err=True)
            raise typer.Exit(1) from None
        except AuthenticationError as e:
            typer.echo(f"❌ Authentication failed: {e}", err=True)
            typer.echo("💡 Check your DOGE_RPC_USER and DOGE_RPC_PASSWORD", err=True)
            raise typer.Exit(1) from None
        except ConnectionError as e:
            typer.echo(f"❌ Connection error: {e}", err=True)
            typer.echo("💡 Make sure dogecoind is running and accessible", err=True)
            raise typer.Exit(1) from None
        except RPCError as e:
            typer.echo(f"❌ RPC error: {e}", err=True)
            raise typer.Exit(1) from None
        except Exception as e:
            typer.echo(f"❌ Unexpected error: {e}", err=True)
            raise typer.Exit(1) from None

    asyncio.run(_send())


@app.command("new-address")
def new_address(
    label: Annotated[
        str,
        typer.Option(help="Label to assign to the new address"),
    ] = "",
    rpc_url: Annotated[
        str | None,
        typer.Option(
            help="Dogecoin RPC URL",
            envvar="DOGE_RPC_URL",
        ),
    ] = None,
    rpc_user: Annotated[
        str | None,
        typer.Option(
            help="RPC username",
            envvar="DOGE_RPC_USER",
        ),
    ] = None,
    rpc_password: Annotated[
        str | None,
        typer.Option(
            help="RPC password",
            envvar="DOGE_RPC_PASSWORD",
        ),
    ] = None,
) -> None:
    """Generate a new Dogecoin address.

    Creates a new receiving address in your wallet.

    Example:
        pydoge new-address --label "mining_rewards"
    """

    async def _new_address() -> None:
        try:
            async with await create_client(rpc_url, rpc_user, rpc_password) as client:
                wallet = Wallet(client)
                addr = await wallet.create_address(label)
                typer.echo(f"✅ New address generated: {addr}")
                if label:
                    typer.echo(f"🏷️  Label: {label}")
        except AuthenticationError as e:
            typer.echo(f"❌ Authentication failed: {e}", err=True)
            typer.echo("💡 Check your DOGE_RPC_USER and DOGE_RPC_PASSWORD", err=True)
            raise typer.Exit(1) from None
        except ConnectionError as e:
            typer.echo(f"❌ Connection error: {e}", err=True)
            typer.echo("💡 Make sure dogecoind is running and accessible", err=True)
            raise typer.Exit(1) from None
        except RPCError as e:
            typer.echo(f"❌ RPC error: {e}", err=True)
            raise typer.Exit(1) from None
        except Exception as e:
            typer.echo(f"❌ Unexpected error: {e}", err=True)
            raise typer.Exit(1) from None

    asyncio.run(_new_address())


def main() -> None:
    """Main entry point for the CLI."""
    app()
