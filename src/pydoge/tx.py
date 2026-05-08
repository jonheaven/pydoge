#!/usr/bin/env python3
"""
Dogecoin Raw Transaction Decoder
Pure Python implementation (no external dependencies).

Supports:
- Legacy transactions
- SegWit (BIP141) transactions
- Doginal / Dogemap inscriptions ("ord" protocol)
"""

import struct
from dataclasses import dataclass, field
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
    """Disassemble a script into human-readable operations and data pushes."""
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


def _parse_witness(tx: bytes, offset: int, vin_count: int) -> Tuple[List[List[bytes]], int]:
    """Parse SegWit witness data. Returns (witness_stacks, new_offset)"""
    witness: List[List[bytes]] = []
    for _ in range(vin_count):
        stack_count, offset = decode_varint(tx, offset)
        stack: List[bytes] = []
        for _ in range(stack_count):
            item_len, offset = decode_varint(tx, offset)
            item = tx[offset:offset + item_len]
            stack.append(item)
            offset += item_len
        witness.append(stack)
    return witness, offset


@dataclass
class DecodedInput:
    txid: str
    vout: int
    scriptSig: str
    scriptSig_asm: List[Dict[str, Any]]
    sequence: int
    witness: Optional[List[bytes]] = None   # for SegWit inputs


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
    is_segwit: bool = False
    witness: Optional[List[List[bytes]]] = field(default=None)  # raw witness stacks

    def get_inscriptions(self) -> List[Dict[str, Any]]:
        """Extract Doginal / inscription data from inputs (if present)."""
        inscriptions = []
        for inp in self.vin:
            script = inp.scriptSig_asm
            # Look for "ord" protocol pattern
            for i, op in enumerate(script):
                if op.get("ascii") == "ord":
                    # Typical Doginal: ord OP_1 content-type OP_0 body
                    content_type = None
                    body = None
                    if i + 4 < len(script):
                        if script[i+1].get("op") == "OP_1" and script[i+2].get("ascii"):
                            content_type = script[i+2]["ascii"]
                        if script[i+3].get("op") == "OP_0" and i+4 < len(script):
                            body_hex = script[i+4].get("hex", "")
                            try:
                                body = bytes.fromhex(body_hex).decode("utf-8", errors="replace")
                            except Exception:
                                body = body_hex
                    inscriptions.append({
                        "input_index": self.vin.index(inp),
                        "content_type": content_type or "unknown",
                        "body": body,
                        "raw_script": script
                    })
                    break
        return inscriptions


def decode_raw_transaction(raw_tx_hex: str) -> DecodedTx:
    """Decode a Dogecoin (Bitcoin-compatible) raw transaction.

    Supports legacy + SegWit (BIP141).
    """"
    tx = bytes.fromhex(raw_tx_hex.strip())
    if len(tx) < 10:
        raise ValueError("Transaction too short")

    offset = 0
    version = struct.unpack("<I", tx[offset:offset+4])[0]
    offset += 4

    # Check for SegWit marker + flag
    is_segwit = False
    if offset + 2 <= len(tx) and tx[offset] == 0x00 and tx[offset+1] == 0x01:
        is_segwit = True
        offset += 2  # skip marker + flag

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

    # Parse witness if SegWit
    witness = None
    if is_segwit:
        witness, offset = _parse_witness(tx, offset, vin_count)
        # attach witness to inputs
        for i, w in enumerate(witness):
            if i < len(vin):
                vin[i].witness = w

    locktime = struct.unpack("<I", tx[offset:offset+4])[0] if offset + 4 <= len(tx) else 0

    return DecodedTx(
        version=version,
        vin=vin,
        vout=vout_list,
        locktime=locktime,
        size=len(tx),
        hex=raw_tx_hex,
        is_segwit=is_segwit,
        witness=witness
    )


def pretty_print_tx(tx: DecodedTx) -> None:
    """Pretty-print a decoded transaction (legacy or SegWit)."""
    print("=" * 72)
    segwit_str = " [SegWit]" if tx.is_segwit else ""
    print(f"DOGECOIN RAW TX DECODER  |  v{tx.version}{segwit_str}  |  {tx.size} bytes")
    print("=" * 72)
    print(f"Locktime: {tx.locktime}")
    print()

    print(f"INPUTS ({len(tx.vin)}):")
    for i, inp in enumerate(tx.vin):
        w_str = " + witness" if inp.witness else ""
        print(f"  [{i}] {inp.txid}:{inp.vout}  seq={inp.sequence}{w_str}")
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

    if tx.is_segwit and tx.witness:
        print(f"\nWITNESS ({len(tx.witness)} stacks):")
        for i, stack in enumerate(tx.witness):
            print(f"  Input {i}: {len(stack)} items")

    # Show inscriptions if any
    inscriptions = tx.get_inscriptions()
    if inscriptions:
        print(f"\n🐕 DOGINAL INSCRIPTIONS ({len(inscriptions)}):")
        for ins in inscriptions:
            print(f"  Content-Type: {ins['content_type']}")
            print(f"  Body preview: {str(ins['body'])[:80]}...")
    print("=" * 72)
