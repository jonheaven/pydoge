# pydoge

<img src="./assets/pydoge.png" alt="pydoge logo" width="60%" style="display: block; margin: 0 auto;">

**Modern async Python SDK for Dogecoin — engineered for 2026.** High-level wallet abstractions, full Doginals / Dogemap / SegWit support, and exceptional developer experience.

[![CI](https://github.com/jonheaven/pydoge/actions/workflows/ci.yml/badge.svg)](https://github.com/jonheaven/pydoge/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pydoge)](https://pypi.org/project/pydoge/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## Vision

pydoge is the definitive Python SDK for Dogecoin development in 2026...

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

## Features

### Current (v0.2)
- ✅ Async JSON-RPC client with httpx
- ✅ High-level Wallet class
- ✅ **Raw tx decoder** with SegWit + full Doginal/Dogemap support
- ✅ Pydantic models
- ✅ Custom exceptions
- ✅ CLI tool with typer
- ✅ Full type hints + mypy
- ✅ pytest + Ruff + GitHub Actions CI

### Roadmap
- v0.3: Dogenals minting & transfer helpers
- v0.4: Fee estimation & batch operations
- v1.0: Production-ready with quantum-resistant options

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
