import re
from typing import TYPE_CHECKING

from .client import Client
from .models import AddressInfo

if TYPE_CHECKING:
    pass


class Wallet:
    """High-level wallet abstraction for Dogecoin operations.

    Provides convenient methods for common wallet operations like
    checking balance, creating addresses, and sending transactions.
    Wraps the lower-level Client for RPC communication.

    Args:
        client: Connected Client instance for RPC calls

    Example:
        async with Client("http://localhost:22555") as client:
            wallet = Wallet(client)
            balance = await wallet.get_balance()
    """

    def __init__(self, client: Client) -> None:
        """Initialize the wallet wrapper.

        Args:
            client: Client instance for RPC communication
        """
        self.client = client

    async def get_balance(self, minconf: int = 1) -> float:
        """Get the total wallet balance.

        Args:
            minconf: Minimum number of confirmations required (default: 1)

        Returns:
            float: Total confirmed balance in DOGE

        Raises:
            ValueError: If minconf is negative
            RPCError: If the RPC call fails
            ConnectionError: If connection fails
        """
        if minconf < 0:
            raise ValueError("minconf must be non-negative")

        return await self.client.getbalance(minconf=minconf)

    async def create_address(self, label: str = "") -> str:
        """Create a new Dogecoin address.

        Args:
            label: Optional label to associate with the address

        Returns:
            str: New Dogecoin address

        Raises:
            RPCError: If the RPC call fails
            ConnectionError: If connection fails
        """
        return await self.client.getnewaddress(label)

    async def send(
        self, address: str, amount: float, comment: str = "", comment_to: str = ""
    ) -> str:
        """Send Dogecoin to an address.

        Args:
            address: Recipient Dogecoin address
            amount: Amount to send in DOGE (must be positive)
            comment: Optional transaction comment
            comment_to: Optional comment for the recipient

        Returns:
            str: Transaction ID (txid)

        Raises:
            ValueError: If amount is not positive or address is invalid
            RPCError: If the RPC call fails
            ConnectionError: If connection fails
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Basic address validation (Dogecoin addresses start with D and are ~34 chars)
        if not re.match(r"^D[A-Za-z0-9]{25,34}$", address):
            raise ValueError("Invalid Dogecoin address format")

        return await self.client.sendtoaddress(address, amount, comment, comment_to)

    async def get_address_info(self, address: str) -> AddressInfo:
        """Get detailed information about an address.

        Args:
            address: Dogecoin address to query

        Returns:
            AddressInfo: Address details including balance and transaction count

        Raises:
            ValueError: If address format is invalid
            RPCError: If the RPC call fails
            ConnectionError: If connection fails
        """
        # Basic address validation
        if not re.match(r"^D[A-Za-z0-9]{25,34}$", address):
            raise ValueError("Invalid Dogecoin address format")

        return await self.client.getaddressinfo(address)
