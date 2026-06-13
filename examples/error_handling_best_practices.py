"""
Error handling best practices with pydoge.

This example demonstrates robust error handling patterns when building
applications with pydoge. It shows:
- Catching and handling different exception types
- Graceful degradation when services are unavailable
- User-friendly error messages
- Logging and monitoring patterns
- Retry logic for transient failures

Requirements:
- pip install pydoge
- Set DOGE_RPC_* environment variables (optional for demo)
"""

import asyncio
import logging
import time
from typing import Optional

from pydoge import Client, Wallet
from pydoge.exceptions import AuthenticationError, ConnectionError, RPCError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RobustWalletService:
    """A wallet service with comprehensive error handling."""

    def __init__(self, rpc_url: str, rpc_user: Optional[str], rpc_password: Optional[str]):
        self.rpc_url = rpc_url
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.client: Optional[Client] = None
        self.wallet: Optional[Wallet] = None
        self.connected = False

    async def connect(self, max_retries: int = 3) -> bool:
        """Connect to dogecoind with retry logic."""
        for attempt in range(max_retries):
            try:
                self.client = Client(self.rpc_url, self.rpc_user, self.rpc_password)
                await self.client.__aenter__()
                self.wallet = Wallet(self.client)
                self.connected = True
                logger.info("Successfully connected to dogecoind")
                return True
            except ConnectionError as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except AuthenticationError as e:
                logger.error(f"Authentication failed: {e}")
                logger.error("Check your DOGE_RPC_USER and DOGE_RPC_PASSWORD")
                return False
            except Exception as e:
                logger.error(f"Unexpected error during connection: {e}")
                return False

        logger.error("Failed to connect after all retries")
        return False

    async def disconnect(self):
        """Safely disconnect from dogecoind."""
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                self.client = None
                self.wallet = None
                self.connected = False

    async def get_balance_safe(self) -> Optional[float]:
        """Get balance with comprehensive error handling."""
        if not self.connected or not self.wallet:
            logger.warning("Wallet not connected")
            return None

        try:
            balance = await self.wallet.get_balance()
            logger.info(f"Current balance: {balance:.8f} DOGE")
            return balance
        except ConnectionError as e:
            logger.error(f"Connection lost while getting balance: {e}")
            self.connected = False
            # Could trigger reconnection logic here
            return None
        except RPCError as e:
            logger.error(f"RPC error getting balance: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting balance: {e}")
            return None

    async def send_safe(self, address: str, amount: float, comment: str = "") -> Optional[str]:
        """Send DOGE with error handling and validation."""
        if not self.connected or not self.wallet:
            logger.error("Wallet not connected")
            return None

        # Pre-flight checks
        if amount <= 0:
            logger.error("Amount must be positive")
            return None

        if not address.startswith('D') or len(address) < 26:
            logger.error("Invalid Dogecoin address format")
            return None

        try:
            # Check balance first
            balance = await self.get_balance_safe()
            if balance is None or balance < amount:
                logger.error(f"Insufficient balance: {balance} < {amount}")
                return None

            txid = await self.wallet.send(address, amount, comment)
            logger.info(f"Successfully sent {amount} DOGE to {address[:16]}...")
            logger.info(f"Transaction ID: {txid}")
            return txid

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return None
        except ConnectionError as e:
            logger.error(f"Connection lost during send: {e}")
            self.connected = False
            return None
        except RPCError as e:
            logger.error(f"RPC error during send: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during send: {e}")
            return None

    async def create_address_safe(self, label: str = "") -> Optional[str]:
        """Create new address with error handling."""
        if not self.connected or not self.wallet:
            logger.error("Wallet not connected")
            return None

        try:
            address = await self.wallet.create_address(label)
            logger.info(f"Created new address: {address}")
            if label:
                logger.info(f"Label: {label}")
            return address
        except ConnectionError as e:
            logger.error(f"Connection lost while creating address: {e}")
            self.connected = False
            return None
        except RPCError as e:
            logger.error(f"RPC error creating address: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating address: {e}")
            return None


async def demonstrate_error_handling():
    """Demonstrate various error handling scenarios."""
    import os

    # Initialize service
    service = RobustWalletService(
        rpc_url=os.getenv("DOGE_RPC_URL", "http://localhost:22555"),
        rpc_user=os.getenv("DOGE_RPC_USER"),
        rpc_password=os.getenv("DOGE_RPC_PASSWORD")
    )

    try:
        # Attempt connection
        connected = await service.connect()
        if not connected:
            logger.error("Could not connect to dogecoind. Please check your configuration.")
            return

        # Demonstrate operations with error handling
        balance = await service.get_balance_safe()
        if balance is not None:
            print(f"Balance: {balance:.8f} DOGE")

        # Try to create an address
        address = await service.create_address_safe("demo_address")
        if address:
            print(f"New address: {address}")

        # Example of sending (commented out for safety)
        # if balance and balance > 0.1:
        #     txid = await service.send_safe(
        #         "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        #         0.1,
        #         "Error handling demo"
        #     )
        #     if txid:
        #         print(f"Sent 0.1 DOGE, TXID: {txid}")

        # Demonstrate error scenarios
        print("\n--- Demonstrating Error Scenarios ---")

        # Try sending with invalid address
        invalid_tx = await service.send_safe("invalid_address", 1.0)
        print(f"Invalid address result: {invalid_tx}")

        # Try sending negative amount
        negative_tx = await service.send_safe("DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", -1.0)
        print(f"Negative amount result: {negative_tx}")

    finally:
        await service.disconnect()


if __name__ == "__main__":
    asyncio.run(demonstrate_error_handling())