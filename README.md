# pydoge

<img src="./assets/pydoge.png" alt="pydoge logo" width="60%" style="display: block; margin: 0 auto;">

**Modern async Python SDK for Dogecoin — engineered for 2026.** High-level wallet abstractions, full Doginals / Dogemap / SegWit support, Dogenals Era 2 helpers, and exceptional developer experience.

[![CI](https://github.com/jonheaven/pydoge/actions/workflows/ci.yml/badge.svg)](https://github.com/jonheaven/pydoge/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pydoge)](https://pypi.org/project/pydoge/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## Vision

pydoge is the definitive Python SDK for Dogecoin development in 2026 — built with uncompromising standards and first-class **Dogenals Era 2** support for Doginals, DMP, and Ð𝕏Ð workflows.

**Core Principles:**
- **Async First**: Everything is async by default for modern Python applications
- **Type Safe**: Full Pydantic models and mypy support for robust development
- **Developer Experience**: Intuitive high-level APIs with low-level power when needed
- **Production Ready**: Built on JSON-RPC with httpx, designed for real applications
- **Dogecoin Native**: APIs designed specifically for Dogecoin's unique characteristics

## Transaction Decoding (v0.2+)

**Pure-Python raw transaction decoder** with full support for:

- Legacy + **SegWit (BIP141)** transactions  
- **Doginal** inscriptions & **Dogemap** tiles ("ord" protocol)
- Script disassembly with ASCII preview

```python
from pydoge import decode_raw_transaction, pretty_print_tx

raw_tx = "0100000001b0f0735c5e3d8056d8b0ac872b5c05923760f176c3be6d010133fbd7ccc356bd1400000032036f7264510a746578742f706c61696e000f363139373632352e646f67656d6170106d6d750a766d3834783979337473755dffffffff01a08601000000000017a9141af89163bb315545982baf0c947ef64ce526ee9e8700000000"

tx = decode_raw_transaction(raw_tx)
pretty_print_tx(tx)

# Extract Doginal data
for ins in tx.get_inscriptions():
    print(ins["content_type"])   # text/plain
    print(ins["body"])           # 6197625.dogemap + payload
```

**Does Dogecoin have SegWit?** Yes — Dogecoin activated SegWit in 2017 (same era as Bitcoin). The decoder fully parses marker/flag + witness stacks.

## Real-World Examples

pydoge comes with comprehensive examples showing production-ready patterns:

### Basic Wallet Operations
[`examples/basic_wallet.py`](examples/basic_wallet.py) - Core wallet functionality with environment configuration.

### Discord Tipping Bot
[`examples/discord_tipping_bot.py`](examples/discord_tipping_bot.py) - Full Discord bot for tipping with Dogecoin.

### FastAPI Wallet Service
[`examples/fastapi_wallet_service.py`](examples/fastapi_wallet_service.py) - REST API for wallet operations with FastAPI.

### Error Handling Best Practices
[`examples/error_handling_best_practices.py`](examples/error_handling_best_practices.py) - Robust error handling, logging, and retry logic.

### Batch Inscription Minting
[`examples/batch_inscriber.py`](examples/batch_inscriber.py) - Production-ready batch inscription minting with confirmation waiting (poached from martinseeger2002 repos).

## Dogenals Era 2 Support

pydoge is the canonical Python library for Doginals and Dogenals development, with first-class support for era 2 protocols.

### Inscription Minting

```python
import asyncio
from pydoge import Client, Inscriber

async def main():
    async with Client("http://localhost:22555", "user", "pass") as client:
        inscriber = Inscriber(client, "your_wif_private_key")

        # Mint a text inscription
        txid = await inscriber.mint(
            "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "text/plain",
            "Hello Doginals!"
        )
        print(f"Inscription TXID: {txid}")

        # Mint a file inscription
        txid = await inscriber.mint(
            "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "image/png",
            "path/to/image.png"
        )
        print(f"File inscription TXID: {txid}")

asyncio.run(main())
```

### DRC-20 Token Operations

```python
from pydoge import Inscriber

# Deploy a DRC-20 token
txid = await inscriber.deploy_drc20(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "MYTOKEN",
    "1000000",  # max supply
    "1000"      # limit per mint
)

# Mint tokens
txids = await inscriber.mint_drc20(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "MYTOKEN",
    "1000",
    repeat=5  # Mint 5 times
)

# Transfer tokens
txid = await inscriber.transfer_drc20(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "MYTOKEN",
    "500"
)
```

### Doginals Era 1 Features

```python
from pydoge import DoginalsHelper

# Initialize helper
helper = DoginalsHelper(inscriber, client)

# Inscribe plain text
txid = await helper.inscribe_text(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "Hello Doginals Era 1!"
)

# Inscribe JSON metadata
txid = await helper.inscribe_json(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    {"name": "My NFT", "description": "A unique digital item"}
)

# Create parent-child relationship
result = await helper.inscribe_parent_child(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",  # parent address
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",  # child address
    "Parent inscription content",
    "Child inscription content"
)

# Inscribe collection item
txid = await helper.inscribe_collection_item(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "My Collection",
    "Rare Item #1",
    {"rarity": "legendary", "power": 100}
)

# Create delegate inscription
txid = await helper.create_delegate_inscription(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "parent_inscription_txid"
)
```

### Dogenals Era 2 Features

```python
from pydoge import DogenalsHelper

# Initialize helper
helper = DogenalsHelper(inscriber, client)

# Deploy bonding curve token
txid = await helper.deploy_bonding_curve(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "CURVE",
    0.001,  # initial price
    {"type": "linear", "slope": 0.0001}
)

# Create ÐMP marketplace listing
txid = await helper.create_dmp_intent(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "inscription_txid_here",
    100.0  # price in DOGE
)

# Inscribe a DogeTag
txid = await helper.inscribe_dogetag(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "myhandle"
)

# Create parent collection
txid = await helper.create_collection_parent(
    "DXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "My NFT Collection",
    {"description": "A collection of unique Doginals"}
)
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

### Current (v0.2)
- ✅ Async JSON-RPC client with httpx
- ✅ High-level Wallet class
- ✅ **Raw tx decoder** with SegWit + full Doginal/Dogemap support
- ✅ Doginals / DMP / Dogenals helpers and inscription tooling
- ✅ Pydantic models
- ✅ Custom exceptions
- ✅ CLI tool with typer
- ✅ Full type hints + mypy
- ✅ pytest + Ruff + GitHub Actions CI

### Roadmap
- **v1.1 (Q2 2026)**: Advanced transaction management with fee estimation and batch operations
- **v1.2 (Q3 2026)**: Multi-wallet support and HD wallet integration
- **v2.1 (2027)**: Quantum-resistant transaction protocols and enhanced security features

## Quickstart

```bash
pip install pydoge
# or uv add pydoge
```

(Original quickstart, CLI, and architecture sections preserved above)

## Development

```bash
git clone https://github.com/jonheaven/pydoge.git
cd pydoge
pip install -e .[dev]
pytest tests/test_tx.py -q   # run tx decoder tests
ruff format .
```

## License

MIT License — see LICENSE for details.
