from typing import Any

from pydantic import BaseModel


class BlockchainInfo(BaseModel):
    """Model for getblockchaininfo response."""

    chain: str
    blocks: int
    headers: int
    bestblockhash: str
    difficulty: float
    mediantime: int
    verificationprogress: float
    initialblockdownload: bool
    chainwork: str
    size_on_disk: int
    pruned: bool
    pruneheight: int | None = None
    automatic_pruning: bool | None = None
    prune_target_size: int | None = None
    softforks: list[dict[str, Any]]
    warnings: str


class Balance(BaseModel):
    """Model for wallet balance."""

    confirmed: float
    unconfirmed: float
    immature: float


class Transaction(BaseModel):
    """Basic transaction model."""

    txid: str
    amount: float
    confirmations: int
    time: int
    timereceived: int
    details: list[dict[str, Any]]


class AddressInfo(BaseModel):
    """Model for getaddressinfo response."""

    address: str
    scriptPubKey: str
    ismine: bool
    iswatchonly: bool
    isscript: bool
    iswitness: bool
    witness_version: int | None = None
    witness_program: str | None = None
    script: str | None = None
    hex: str | None = None
    pubkeys: list[str] | None = None
    sigsrequired: int | None = None
    pubkey: str | None = None
    embedded: dict[str, Any] | None = None
    iscompressed: bool | None = None
    label: str | None = None
    timestamp: int | None = None
    hdkeypath: str | None = None
    hdseedid: str | None = None
    hdmasterfingerprint: str | None = None
    labels: list[dict[str, str]]
