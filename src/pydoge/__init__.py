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
from .tx import decode_raw_transaction, decode_script, pretty_print_tx, DecodedTx
from .wallet import Wallet

__all__ = [
    # Core classes
    "Client",
    "Wallet",
    # Tx decoder
    "decode_raw_transaction",
    "decode_script",
    "pretty_print_tx",
    "DecodedTx",
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
