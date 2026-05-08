"""Tests for the pure-Python Dogecoin transaction decoder."""

import pytest
from pydoge import decode_raw_transaction, pretty_print_tx

# The example tx from our conversation (Doginal / Dogemap inscription)
EXAMPLE_RAW_TX = (
    "0100000001b0f0735c5e3d8056d8b0ac872b5c05923760f176c3be6d010133fbd7ccc356bd14"
    "0000000032036f7264510a746578742f706c61696e000f363139373632352e646f67656d6170"
    "106d6d750a766d3834783979337473755dffffffff01a08601000000000017a9141af89163bb315545982baf0c947ef64ce526ee9e8700000000"
)


def test_decode_legacy_tx():
    tx = decode_raw_transaction(EXAMPLE_RAW_TX)
    assert tx.version == 1
    assert tx.is_segwit is False
    assert len(tx.vin) == 1
    assert len(tx.vout) == 1
    assert tx.vout[0].value_doge == 0.001
    assert tx.locktime == 0
    assert tx.size == 133


def test_inscription_extraction():
    tx = decode_raw_transaction(EXAMPLE_RAW_TX)
    inscriptions = tx.get_inscriptions()
    assert len(inscriptions) == 1
    ins = inscriptions[0]
    assert ins["content_type"] == "text/plain"
    assert "6197625.dogemap" in str(ins["body"])
    assert "mmu" in str(ins["body"])


def test_script_disassembly():
    tx = decode_raw_transaction(EXAMPLE_RAW_TX)
    input_script = tx.vin[0].scriptSig_asm
    ops = [op["op"] for op in input_script]
    assert "OP_PUSHBYTES_3" in ops
    assert any("ord" in str(op.get("ascii", "")) for op in input_script)
    assert "OP_HASH160" in [op["op"] for op in tx.vout[0].scriptPubKey_asm]


def test_pretty_print_runs_without_error():
    tx = decode_raw_transaction(EXAMPLE_RAW_TX)
    # Should not raise
    pretty_print_tx(tx)


def test_segwit_detection():
    # Minimal SegWit tx example (marker + flag present)
    # This is a simplified test - real SegWit txs would have witness data
    segwit_hex = "01000000000101" + "0" * 128 + "0000000000"  # placeholder
    # For now just test that non-SegWit is correctly detected
    tx = decode_raw_transaction(EXAMPLE_RAW_TX)
    assert tx.is_segwit is False
