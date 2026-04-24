from typing import Any

import httpx

from .exceptions import AuthenticationError, ConnectionError, RPCError
from .models import AddressInfo, BlockchainInfo


class Client:
    """Async JSON-RPC 2.0 client for Dogecoin Core.

    Provides a high-level interface to Dogecoin Core's JSON-RPC API,
    handling connection management, authentication, and error handling.

    Args:
        url: RPC endpoint URL (e.g., "http://localhost:22555")
        user: RPC username (optional, for authentication)
        password: RPC password (optional, for authentication)
        timeout: Request timeout in seconds (default: 30.0)

    Example:
        async with Client("http://localhost:22555", "user", "pass") as client:
            info = await client.getblockchaininfo()
    """

    def __init__(
        self,
        url: str,
        user: str | None = None,
        password: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the RPC client.

        Args:
            url: RPC endpoint URL
            user: RPC username for authentication
            password: RPC password for authentication
            timeout: Request timeout in seconds
        """
        self.url = url
        self.auth = (user, password) if user and password else None
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._id_counter = 0

    async def __aenter__(self) -> "Client":
        """Enter async context manager."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        """Exit async context manager."""
        await self.close()

    async def connect(self) -> None:
        """Establish connection to the RPC server.

        Creates an httpx.AsyncClient instance if not already connected.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                auth=self.auth,
                timeout=self.timeout,
            )

    async def close(self) -> None:
        """Close the connection to the RPC server.

        Cleans up the httpx client instance.
        """
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _call(
        self, method: str, *params: Any
    ) -> dict[str, Any] | list[Any] | str | int | float | bool | None:
        """Make a JSON-RPC 2.0 call to the server.

        Args:
            method: RPC method name
            *params: Variable arguments for the RPC call

        Returns:
            The RPC result value

        Raises:
            RPCError: If the server returns an error
            AuthenticationError: If authentication fails
            ConnectionError: If connection or request fails
        """
        if self._client is None:
            await self.connect()

        if self._client is None:
            raise ConnectionError("Failed to establish connection")

        self._id_counter += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": list(params),
            "id": self._id_counter,
        }

        try:
            response = await self._client.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            try:
                data: dict[str, Any] = response.json()
            except ValueError as e:
                raise ConnectionError(f"Invalid JSON response: {e}") from e

            # Validate response ID
            if data.get("id") != payload["id"]:
                raise RPCError(-32600, f"Response ID mismatch for method '{method}'")

            # Check for RPC errors
            if "error" in data and data["error"] is not None:
                error = data["error"]
                if isinstance(error, dict):
                    code = error.get("code", -1)
                    message = error.get("message", "Unknown RPC error")
                    raise RPCError(code, f"{method}: {message}")
                else:
                    raise RPCError(-1, f"{method}: {error}")

            return data.get("result")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid RPC credentials") from e
            elif e.response.status_code >= 400:
                try:
                    error_data = e.response.json()
                    if isinstance(error_data, dict) and "error" in error_data:
                        error = error_data["error"]
                        if isinstance(error, dict):
                            message = error.get("message", str(e))
                        else:
                            message = str(error)
                    else:
                        message = e.response.text or str(e)
                except ValueError:
                    message = e.response.text or str(e)
                raise ConnectionError(
                    f"HTTP {e.response.status_code} for {method}: {message}"
                ) from e
            raise ConnectionError(f"HTTP error for {method}: {e}") from e
        except httpx.RequestError as e:
            raise ConnectionError(f"Request failed for {method}: {e}") from e

    async def getblockchaininfo(self) -> BlockchainInfo:
        """Get blockchain information.

        Returns:
            BlockchainInfo: Current blockchain state including blocks, difficulty, etc.

        Raises:
            RPCError: If the RPC call fails
            ConnectionError: If connection fails
        """
        result = await self._call("getblockchaininfo")
        if not isinstance(result, dict):
            raise RPCError(-32603, "Invalid response format for getblockchaininfo")
        return BlockchainInfo(**result)

    async def getaddressinfo(self, address: str) -> AddressInfo:
        """Get information about an address.

        Args:
            address: Dogecoin address to query

        Returns:
            AddressInfo: Address details including balance, transactions, etc.

        Raises:
            RPCError: If the RPC call fails
            ConnectionError: If connection fails
        """
        result = await self._call("getaddressinfo", address)
        if not isinstance(result, dict):
            raise RPCError(-32603, "Invalid response format for getaddressinfo")
        return AddressInfo(**result)

    async def getbalance(self, account: str = "*", minconf: int = 1) -> float:
        """Get wallet balance.

        Args:
            account: Account name ("*" for all accounts)
            minconf: Minimum confirmations required

        Returns:
            float: Total balance in DOGE

        Raises:
            RPCError: If the RPC call fails
            ConnectionError: If connection fails
        """
        result = await self._call("getbalance", account, minconf)
        if isinstance(result, (str, int, float)):
            try:
                return float(result)
            except (TypeError, ValueError) as e:
                raise RPCError(-32603, f"Invalid balance format: {result}") from e
        elif result is None:
            return 0.0
        else:
            raise RPCError(-32603, f"Invalid balance format: {result}")

    async def getnewaddress(self, label: str = "") -> str:
        """Generate a new address.

        Args:
            label: Optional label for the address

        Returns:
            str: New Dogecoin address

        Raises:
            RPCError: If the RPC call fails
            ConnectionError: If connection fails
        """
        result = await self._call("getnewaddress", label)
        if not isinstance(result, str):
            raise RPCError(-32603, f"Invalid address format: {result}")
        return result

    async def sendtoaddress(
        self, address: str, amount: float, comment: str = "", comment_to: str = ""
    ) -> str:
        """Send Dogecoin to an address.

        Args:
            address: Recipient address
            amount: Amount to send in DOGE
            comment: Transaction comment
            comment_to: Comment for recipient

        Returns:
            str: Transaction ID

        Raises:
            RPCError: If the RPC call fails
            ConnectionError: If connection fails
        """
        result = await self._call(
            "sendtoaddress", address, str(amount), comment, comment_to
        )
        if not isinstance(result, str):
            raise RPCError(-32603, f"Invalid transaction ID format: {result}")
        return result
