__version__ = "0.1.0"

from .client import Client
from .exceptions import (
    AuthenticationError,
    ConnectionError,
    PydogeError,
    RPCError,
)
from .models import (
    AddressInfo,
    Balance,
    BlockchainInfo,
    Transaction,
)
from .wallet import Wallet

__all__ = [
    # Core classes
    "Client",
    "Wallet",
    # Exceptions
    "PydogeError",
    "RPCError",
    "ConnectionError",
    "AuthenticationError",
    # Models
    "BlockchainInfo",
    "AddressInfo",
    "Balance",
    "Transaction",
    # Version
    "__version__",
]
