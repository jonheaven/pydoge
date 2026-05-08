#!/usr/bin/env python3
"""
Dogecoin Raw Transaction Decoder
Pure Python implementation (no external dependencies).

Supports legacy transactions + Doginal / Dogemap inscriptions.
"""

import struct
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional


OPCODE_NAMES: Dict[int, str] = {
    0x00: "OP_0",
    0x4f: "OP_1NEGATE",
    0x51: "OP_1", 0x52: "OP_2", 0x53: "OP_3", 0x54: "OP_4", 0x55: "OP_5",
    0x56: "OP_6", 0x57: "OP_7", 0x58: "OP_8", 0x59: "OP_9", 0x5a: "OP_10",
    0x5b: "OP_11", 0x5c: "OP_12", 0x5d: "OP_13", 0x5e: "OP_14", 0x5f: "OP_15", 0x60: "OP_16",
    0x61: "OP_NOP", 0x63: "OP_IF", 0x64: "OP_NOTIF", 0x67: "OP_ELSE", 0x68: "OP_ENDIF",
    0x69: "OP_VERIFY", 0x6a: "OP_RETURN",
    0x76: "OP_DUP", 0x87: "OP_EQUAL", 0x88: "OP_EQUALVERIFY",
    0xa9: "OP_HASH160", 0xac: "OP_CHECKSIG",
    0xaf: "OP_RIPEMD160", 0xb0: "OP_SHA1", 0xb1: "OP_SHA256", 0xb2: "OP_HASH256",
    0xb5: "OP_CHECKSIG", 0xb6: "OP_CHECKSIGVERIFY",
}


def decode_varint(data: bytes, offset: int) -> Tuple[int, int]:
    """Decode Bitcoin/Dogecoin varint (CompactSize)."""
    if offset >= len(data):
        raise ValueError("Unexpected end of data")
    first = data[offset]
    if first < 0xfd:
        return first, offset + 1
    elif first == 0xfd:
        return struct.unpack("<H", data[offset+1:offset+3])[0], offset + 3
    elif first == 0xfe:
        return struct.unpack("<I", data[offset+1:offset+5])[0], offset + 5
    else:
        return struct.unpack("<Q", data[offset+1:offset+9])[0], offset + 9


def decode_script(script_hex: str) -> List[Dict[str, Any]]:
    """Disassemble a script (scriptSig or scriptPubKey) into ops + data pushes."""
    if not script_hex:
        return []
    try:
        script = bytes.fromhex(script_hex)
    except ValueError:
        return [{"error": "invalid hex"}]

    ops: List[Dict[str, Any]] = []
    i = 0
    while i < len(script):
        opcode = script[i]
        i += 1
        if 0x01 <= opcode <= 0x4b:  # push N bytes
            n = opcode
            if i + n > len(script):
                ops.append({"op": f"OP_PUSHBYTES_{n}", "error": "truncated"})
                break
            data = script[i:i + n]
            ascii_str = None
            try:
                ascii_str = data.decode("ascii", errors="replace")
                if not all(32 <= ord(c) < 127 or c in "\n\r\t" for c in ascii_str):
                    ascii_str = None
            except Exception:
                pass
            ops.append({
                "op": f"OP_PUSHBYTES_{n}",
                "hex": data.hex(),
                "ascii": ascii_str
            })
            i += n
        else:
            name = OPCODE_NAMES.get(opcode, f"OP_UNKNOWN_{opcode:02x}")
            ops.append({"op": name, "opcode": opcode})
    return ops


@dataclass
class DecodedInput:
    txid: str
    vout: int
    scriptSig: str
    scriptSig_asm: List[Dict[str, Any]]
    sequence: int


@dataclass
class DecodedOutput:
    value_doge: float
    value_sats: int
    scriptPubKey: str
    scriptPubKey_asm: List[Dict[str, Any]]


@dataclass
class DecodedTx:
    version: int
    vin: List[DecodedInput]
    vout: List[DecodedOutput]
    locktime: int
    size: int
    hex: str


def decode_raw_transaction(raw_tx_hex: str) -> DecodedTx:
    """Decode a Dogecoin (or Bitcoin) raw transaction hex."""
    tx = bytes.fromhex(raw_tx_hex.strip())
    if len(tx) < 10:
        raise ValueError("Transaction too short")

    offset = 0
    version = struct.unpack("<I", tx[offset:offset+4])[0]
    offset += 4

    vin_count, offset = decode_varint(tx, offset)
    vin: List[DecodedInput] = []
    for _ in range(vin_count):
        prev_txid = tx[offset:offset+32][::-1].hex()
        offset += 32
        vout = struct.unpack("<I", tx[offset:offset+4])[0]
        offset += 4
        slen, offset = decode_varint(tx, offset)
        script_sig = tx[offset:offset+slen].hex()
        offset += slen
        seq = struct.unpack("<I", tx[offset:offset+4])[0]
        offset += 4
        vin.append(DecodedInput(
            txid=prev_txid,
            vout=vout,
            scriptSig=script_sig,
            scriptSig_asm=decode_script(script_sig),
            sequence=seq
        ))

    vout_count, offset = decode_varint(tx, offset)
    vout_list: List[DecodedOutput] = []
    for _ in range(vout_count):
        value = struct.unpack("<Q", tx[offset:offset+8])[0]
        offset += 8
        slen, offset = decode_varint(tx, offset)
        spk = tx[offset:offset+slen].hex()
        offset += slen
        vout_list.append(DecodedOutput(
            value_doge=value / 100_000_000,
            value_sats=value,
            scriptPubKey=spk,
            scriptPubKey_asm=decode_script(spk)
        ))

    locktime = struct.unpack("<I", tx[offset:offset+4])[0] if offset + 4 <= len(tx) else 0

    return DecodedTx(
        version=version,
        vin=vin,
        vout=vout_list,
        locktime=locktime,
        size=len(tx),
        hex=raw_tx_hex
    )


def pretty_print_tx(tx: DecodedTx) -> None:
    """Pretty-print a decoded transaction."""
    print("=" * 70)
    print(f"DOGECOIN RAW TX DECODER  |  v{tx.version}  |  {tx.size} bytes")
    print("=" * 70)
    print(f"Locktime: {tx.locktime}")
    print()

    print(f"INPUTS ({len(tx.vin)}):")
    for i, inp in enumerate(tx.vin):
        print(f"  [{i}] {inp.txid}:{inp.vout}  seq={inp.sequence}")
        for op in inp.scriptSig_asm:
            if op.get("ascii"):
                print(f"      {op['op']}: \"{op['ascii']}\"")
            else:
                print(f"      {op['op']}")

    print(f"\nOUTPUTS ({len(tx.vout)}):")
    for i, out in enumerate(tx.vout):
        print(f"  [{i}] {out.value_doge:.8f} DOGE")
        for op in out.scriptPubKey_asm:
            print(f"      {op['op']}")
    print("=" * 70)
