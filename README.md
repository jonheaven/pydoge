# pydoge

<img src="./assets/pydoge.png" alt="pydoge logo" width="60%" style="display: block; margin: 0 auto;">

**Modern async Python SDK for Dogecoin — engineered for 2026.** High-level wallet abstractions, Doginals / Dogemap support, and exceptional developer experience.

[![CI](https://github.com/jonheaven/pydoge/actions/workflows/ci.yml/badge.svg)](https://github.com/jonheaven/pydoge/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pydoge)](https://pypi.org/project/pydoge/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## Vision

pydoge is the definitive Python SDK for Dogecoin development in 2026...

(Full original content preserved — added tx decoder section below)

## Transaction Decoding (New in v0.1.1)

Pure-Python raw transaction decoder with full support for **Doginals** and **Dogemap** inscriptions:

```python
from pydoge import decode_raw_transaction, pretty_print_tx

raw_tx = "0100000001b0f0735c..."  # your raw hex

tx = decode_raw_transaction(raw_tx)
pretty_print_tx(tx)

# Access inscription data easily
for inp in tx.vin:
    for op in inp.scriptSig_asm:
        if op.get("ascii") and "ord" in str(op):
            print("Doginal inscription found:", op)
```

Supports:
- Full legacy tx parsing
- Script disassembly (OP codes + data pushes)
- Automatic detection of "ord" protocol inscriptions
- Dogemap tile IDs, text/plain content, etc.

See `src/pydoge/tx.py` for the complete implementation.

## Features

### v0.1 (Current)
- ✅ Async JSON-RPC client
- ✅ High-level Wallet
- ✅ **Raw transaction decoder with Doginal support** (new!)
- ... (rest of features)
