__version__ = "0.1.0"

from .client import Client
from .exceptions import (
    AuthenticationError,
    ConnectionError,
    PydogeError,
    RPCError,
    ValidationError,
)
from .wallet import Wallet

__all__ = [
    "Client",
    "Wallet",
    "PydogeError",
    "RPCError",
    "ConnectionError",
    "ValidationError",
    "AuthenticationError",
]
