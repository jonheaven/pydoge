from .client import Client
from .models import AddressInfo


class Wallet:
    """High-level wallet abstraction for Dogecoin."""

    def __init__(self, client: Client) -> None:
        self.client = client

    async def get_balance(self, minconf: int = 1) -> float:
        """Get total wallet balance."""
        return await self.client.getbalance(minconf=minconf)

    async def create_address(self, label: str = "") -> str:
        """Create a new address."""
        return await self.client.getnewaddress(label)

    async def send(
        self, address: str, amount: float, comment: str = "", comment_to: str = ""
    ) -> str:
        """Send Dogecoin to an address."""
        return await self.client.sendtoaddress(address, amount, comment, comment_to)

    async def get_address_info(self, address: str) -> AddressInfo:
        """Get information about an address."""
        return await self.client.getaddressinfo(address)
