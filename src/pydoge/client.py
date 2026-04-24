from typing import Any

import httpx

from .exceptions import AuthenticationError, ConnectionError, RPCError
from .models import AddressInfo, BlockchainInfo


class Client:
    """Async JSON-RPC client for Dogecoin Core."""

    def __init__(
        self,
        url: str,
        user: str | None = None,
        password: str | None = None,
        timeout: float = 30.0,
    ):
        self.url = url
        self.auth = (user, password) if user and password else None
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._id_counter = 0

    async def __aenter__(self) -> "Client":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        await self.close()

    async def connect(self) -> None:
        """Establish connection."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                auth=self.auth,
                timeout=self.timeout,
            )

    async def close(self) -> None:
        """Close connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _call(self, method: str, *params: Any) -> Any:
        """Make RPC call."""
        if self._client is None:
            await self.connect()

        assert self._client is not None

        self._id_counter += 1
        payload = {
            "jsonrpc": "1.1",
            "method": method,
            "params": params,
            "id": self._id_counter,
        }

        try:
            response = await self._client.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data and data["error"] is not None:
                error = data["error"]
                raise RPCError(
                    error.get("code", -1), error.get("message", "Unknown error")
                )

            return data.get("result")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid credentials") from e
            raise ConnectionError(
                f"HTTP {e.response.status_code}: {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise ConnectionError(f"Request failed: {e}") from e

    async def getblockchaininfo(self) -> BlockchainInfo:
        """Get blockchain information."""
        result = await self._call("getblockchaininfo")
        return BlockchainInfo(**result)

    async def getaddressinfo(self, address: str) -> AddressInfo:
        """Get information about an address."""
        result = await self._call("getaddressinfo", address)
        return AddressInfo(**result)

    async def getbalance(self, account: str = "*", minconf: int = 1) -> float:
        """Get wallet balance."""
        result = await self._call("getbalance", account, minconf)
        return float(result)

    async def getnewaddress(self, label: str = "") -> str:
        """Generate new address."""
        result = await self._call("getnewaddress", label)
        return str(result)

    async def sendtoaddress(
        self, address: str, amount: float, comment: str = "", comment_to: str = ""
    ) -> str:
        """Send to address."""
        result = await self._call(
            "sendtoaddress", address, str(amount), comment, comment_to
        )
        return str(result)
