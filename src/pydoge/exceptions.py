from typing import Any


class PydogeError(Exception):
    """Base exception for pydoge."""

    pass


class RPCError(PydogeError):
    """Raised when RPC call fails."""

    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"RPC error {code}: {message}")


class ConnectionError(PydogeError):
    """Raised when connection to dogecoind fails."""

    pass


class ValidationError(PydogeError):
    """Raised when input validation fails."""

    pass


class AuthenticationError(PydogeError):
    """Raised when authentication fails."""

    pass
