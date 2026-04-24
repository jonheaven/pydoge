import re
from typing import Any

from pydantic import BaseModel, Field, field_validator


class BlockchainInfo(BaseModel):
    """Model for getblockchaininfo RPC response.

    Contains information about the current state of the blockchain.
    """

    chain: str = Field(..., description="Network name (main, test, regtest)")
    blocks: int = Field(..., ge=0, description="Current block height")
    headers: int = Field(..., ge=0, description="Current header count")
    bestblockhash: str = Field(..., description="Hash of the best block")
    difficulty: float = Field(..., gt=0, description="Current difficulty")
    mediantime: int = Field(..., ge=0, description="Median time of the best block")
    verificationprogress: float = Field(..., ge=0, le=1, description="Verification progress (0-1)")
    initialblockdownload: bool = Field(..., description="Whether in initial block download")
    chainwork: str = Field(..., description="Total chain work")
    size_on_disk: int = Field(..., ge=0, description="Size of blockchain on disk in bytes")
    pruned: bool = Field(..., description="Whether blockchain is pruned")
    pruneheight: int | None = Field(None, ge=0, description="Prune height")
    automatic_pruning: bool | None = Field(None, description="Whether automatic pruning is enabled")
    prune_target_size: int | None = Field(None, ge=0, description="Target prune size in bytes")
    softforks: list[dict[str, Any]] = Field(default_factory=list, description="Active softforks")
    warnings: str = Field("", description="Warning messages")

    @field_validator("bestblockhash")
    @classmethod
    def validate_blockhash(cls, v: str) -> str:
        """Validate block hash format (64 hex characters)."""
        if not re.match(r"^[a-fA-F0-9]{64}$", v):
            raise ValueError("Invalid block hash format")
        return v


class Balance(BaseModel):
    """Model for wallet balance breakdown.

    Provides detailed balance information including confirmed,
    unconfirmed, and immature coins.
    """

    confirmed: float = Field(..., ge=0, description="Confirmed balance")
    unconfirmed: float = Field(..., ge=0, description="Unconfirmed balance")
    immature: float = Field(..., ge=0, description="Immature balance (e.g., mining rewards)")


class Transaction(BaseModel):
    """Model for basic transaction information.

    Represents a wallet transaction with essential details.
    """

    txid: str = Field(..., description="Transaction ID")
    amount: float = Field(..., description="Transaction amount (positive for received, negative for sent)")
    confirmations: int = Field(..., ge=0, description="Number of confirmations")
    time: int = Field(..., ge=0, description="Transaction time (Unix timestamp)")
    timereceived: int = Field(..., ge=0, description="Time received (Unix timestamp)")
    details: list[dict[str, Any]] = Field(default_factory=list, description="Transaction details")

    @field_validator("txid")
    @classmethod
    def validate_txid(cls, v: str) -> str:
        """Validate transaction ID format (64 hex characters)."""
        if not re.match(r"^[a-fA-F0-9]{64}$", v):
            raise ValueError("Invalid transaction ID format")
        return v


class AddressInfo(BaseModel):
    """Model for getaddressinfo RPC response.

    Contains detailed information about a Dogecoin address.
    """

    address: str = Field(..., description="Dogecoin address")
    scriptPubKey: str = Field(..., description="Script public key")
    ismine: bool = Field(..., description="Whether address belongs to wallet")
    iswatchonly: bool = Field(..., description="Whether address is watch-only")
    isscript: bool = Field(..., description="Whether address is a script")
    iswitness: bool = Field(..., description="Whether address is a witness address")
    witness_version: int | None = Field(None, ge=0, description="Witness version")
    witness_program: str | None = Field(None, description="Witness program")
    script: str | None = Field(None, description="Script type")
    hex: str | None = Field(None, description="Script hex")
    pubkeys: list[str] | None = Field(None, description="Public keys")
    sigsrequired: int | None = Field(None, ge=0, description="Signatures required")
    pubkey: str | None = Field(None, description="Public key")
    embedded: dict[str, Any] | None = Field(None, description="Embedded script info")
    iscompressed: bool | None = Field(None, description="Whether public key is compressed")
    label: str | None = Field(None, description="Address label")
    timestamp: int | None = Field(None, ge=0, description="Address creation timestamp")
    hdkeypath: str | None = Field(None, description="HD key path")
    hdseedid: str | None = Field(None, description="HD seed ID")
    hdmasterfingerprint: str | None = Field(None, description="HD master fingerprint")
    labels: list[dict[str, str]] = Field(default_factory=list, description="Address labels")

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate Dogecoin address format."""
        if not re.match(r"^D[A-Za-z0-9]{25,34}$", v):
            raise ValueError("Invalid Dogecoin address format")
        return v

    @field_validator("pubkey", "witness_program", "hex")
    @classmethod
    def validate_hex_fields(cls, v: str | None) -> str | None:
        """Validate hex string fields."""
        if v is not None and not re.match(r"^[a-fA-F0-9]*$", v):
            raise ValueError("Invalid hex format")
        return v

    @field_validator("pubkeys")
    @classmethod
    def validate_pubkeys(cls, v: list[str] | None) -> list[str] | None:
        """Validate public key list."""
        if v is not None:
            for pubkey in v:
                if not re.match(r"^[a-fA-F0-9]*$", pubkey):
                    raise ValueError("Invalid public key format")
        return v
