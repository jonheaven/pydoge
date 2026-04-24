# pydoge

<img src="./assets/pydoge.png" alt="pydoge logo" width="60%" style="display: block; margin: 0 auto;">

**Modern async Python SDK for Dogecoin — engineered for 2026.** High-level wallet abstractions, Dogenals support, quantum-resistant transactions, and exceptional developer experience.

[![CI](https://github.com/jonheaven/pydoge/actions/workflows/ci.yml/badge.svg)](https://github.com/jonheaven/pydoge/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pydoge)](https://pypi.org/project/pydoge/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## Vision

pydoge is the definitive Python SDK for Dogecoin development in 2026, engineered with uncompromising standards. We meticulously analyze leading libraries, distill their finest patterns, and forge a solution that sets new benchmarks for quality and performance.

**Core Principles:**
- **Async Excellence**: Fully asynchronous architecture optimized for high-performance Python applications
- **Type Safety**: Comprehensive Pydantic validation and mypy integration for robust development
- **Developer-Centric**: Intuitive high-level APIs with granular low-level control
- **Future-Proof**: Native support for Dogenals, inscriptions, and quantum-resistant transactions
- **Enterprise-Ready**: Leverages libdogecoin with seamless JSON-RPC fallback for maximum compatibility

**Why Choose pydoge?**
- Precision-crafted code with the familiarity of web3.py, optimized for Dogecoin
- Robust error management with detailed custom exceptions
- Comprehensive documentation with verified, working examples
- Enterprise-grade project structure from inception
- Unwavering commitment to code quality and maintainability

## Quickstart

### Installation

```bash
pip install pydoge
# or with uv
uv add pydoge
```

### Basic Usage

```python
import asyncio
from pydoge import Client, Wallet

async def main():
    # Connect to dogecoind
    async with Client(
        url="http://localhost:22555",
        user="your_rpc_user",
        password="your_rpc_password"
    ) as client:
        # High-level wallet
        wallet = Wallet(client)

        # Get balance
        balance = await wallet.get_balance()
        print(f"Balance: {balance} DOGE")

        # Create new address
        address = await wallet.create_address("my_label")
        print(f"New address: {address}")

        # Send DOGE
        txid = await wallet.send("DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", 1.0)
        print(f"Sent 1 DOGE, TXID: {txid}")

        # Low-level blockchain info
        info = await client.getblockchaininfo()
        print(f"Current block: {info.blocks}")

asyncio.run(main())
```

### CLI Tool

pydoge comes with a powerful CLI tool:

```bash
# Install with CLI support
pip install pydoge[cli]

# Get balance
pydoge balance --rpc-user your_user --rpc-password your_pass

# Send DOGE
pydoge send DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX 1.0 --rpc-user your_user --rpc-password your_pass

# Generate new address
pydoge new-address --label "my_wallet"
```

## Features

### v1.0 (Current)
- ✅ Async JSON-RPC client with httpx
- ✅ High-level Wallet class (balance, send, addresses)
- ✅ Pydantic models for all responses
- ✅ Custom exceptions for error handling
- ✅ CLI tool with typer
- ✅ Full type hints and mypy support
- ✅ Comprehensive test suite with pytest
- ✅ Ruff linting and formatting
- ✅ GitHub Actions CI

### Roadmap
- **v1.1 (Q2 2026)**: Advanced transaction management with fee estimation and batch operations
- **v1.2 (Q3 2026)**: Multi-wallet support and HD wallet integration
- **v2.0 (Q4 2026)**: Full Dogenals implementation and inscription support
- **v2.1 (2027)**: Quantum-resistant transaction protocols and enhanced security features

## Architecture

```
pydoge/
├── client.py      # Core async RPC client
├── wallet.py      # High-level wallet abstraction
├── models.py      # Pydantic data models
├── exceptions.py  # Custom error classes
├── cli.py         # Command-line interface
└── __init__.py    # Package exports
```

**Design Decisions:**
- **src/ layout**: Modern Python packaging
- **Async everywhere**: httpx for HTTP, asyncio for concurrency
- **Pydantic v2**: Type-safe data validation
- **Context managers**: Automatic connection handling
- **Dynamic methods**: Inspired by web3.py's clean API

## Development

### Setup

```bash
# Clone and setup
git clone https://github.com/jonheaven/pydoge.git
cd pydoge

# Install with dev dependencies
pip install -e .[dev]
# or uv sync

# Run tests
pytest

# Lint and format
ruff check .
ruff format .

# Type check
mypy src
```

### Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Guidelines:**
- Follow the existing code style (ruff handles this)
- Add tests for new features
- Update documentation
- Use conventional commits

### Testing

pydoge uses regtest for integration tests. To run the full suite:

```bash
# Unit tests (mocked)
pytest tests/ -v

# Integration tests (requires dogecoind regtest)
pytest tests/ -m integration --regtest
```

## Ecosystem Inspiration

pydoge stands on the shoulders of giants. We studied and improved upon:

- **libdogecoin**: Core C library for low-level crypto
- **web3.py**: Async SDK patterns and clean API design
- **python-bitcoinrpc**: RPC client foundations
- **dogecoin-python**: Existing Python bindings
- **eth-account**: Wallet abstraction patterns

## License

MIT License - see [LICENSE](LICENSE) for details.

## Community

- **GitHub**: [https://github.com/jonheaven/pydoge](https://github.com/jonheaven/pydoge)
- **Issues**: [https://github.com/jonheaven/pydoge/issues](https://github.com/jonheaven/pydoge/issues)
- **Discord**: Join the Dogecoin Foundation Discord

---

Built for the Dogecoin ecosystem.
