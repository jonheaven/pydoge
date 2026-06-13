"""
FastAPI service with pydoge wallet endpoints.

This example demonstrates building a REST API for Dogecoin wallet operations
using FastAPI and pydoge. It shows:
- Async endpoint handlers with FastAPI
- Pydantic request/response models
- Error handling with HTTP status codes
- Dependency injection for wallet access
- Environment-based configuration

Requirements:
- pip install fastapi uvicorn pydoge
- Set DOGE_RPC_* environment variables
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

from pydoge import Client, Wallet


class SendRequest(BaseModel):
    """Request model for sending DOGE."""
    address: str = Field(..., description="Recipient Dogecoin address")
    amount: float = Field(..., gt=0, description="Amount to send in DOGE")
    comment: Optional[str] = Field(None, description="Transaction comment")
    comment_to: Optional[str] = Field(None, description="Comment for recipient")


class TransactionResponse(BaseModel):
    """Response model for transaction operations."""
    txid: str = Field(..., description="Transaction ID")
    amount: float = Field(..., description="Amount sent")
    address: str = Field(..., description="Recipient address")


class AddressResponse(BaseModel):
    """Response model for address generation."""
    address: str = Field(..., description="Generated Dogecoin address")
    label: Optional[str] = Field(None, description="Address label")


class BalanceResponse(BaseModel):
    """Response model for balance queries."""
    balance: float = Field(..., description="Current balance in DOGE")
    confirmed: bool = Field(True, description="Whether balance is confirmed")


# Global instances
client: Optional[Client] = None
wallet: Optional[Wallet] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for wallet setup/cleanup."""
    global client, wallet

    # Setup
    rpc_url = os.getenv("DOGE_RPC_URL", "http://localhost:22555")
    rpc_user = os.getenv("DOGE_RPC_USER")
    rpc_password = os.getenv("DOGE_RPC_PASSWORD")

    if rpc_user and rpc_password:
        try:
            client = Client(rpc_url, rpc_user, rpc_password)
            await client.__aenter__()
            wallet = Wallet(client)
            print("✅ Wallet connected successfully")
        except Exception as e:
            print(f"❌ Failed to connect wallet: {e}")
    else:
        print("⚠️  DOGE_RPC_USER and DOGE_RPC_PASSWORD not set")

    yield

    # Cleanup
    if client:
        await client.__aexit__(None, None, None)


app = FastAPI(
    title="Dogecoin Wallet API",
    description="REST API for Dogecoin wallet operations using pydoge",
    version="1.0.0",
    lifespan=lifespan
)


async def get_wallet() -> Wallet:
    """Dependency to get wallet instance."""
    if not wallet:
        raise HTTPException(status_code=503, detail="Wallet not connected")
    return wallet


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dogecoin-wallet-api"}


@app.get("/balance", response_model=BalanceResponse)
async def get_balance(wallet: Wallet = Depends(get_wallet)):
    """Get current wallet balance."""
    try:
        balance = await wallet.get_balance()
        return BalanceResponse(balance=balance, confirmed=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get balance: {e}")


@app.post("/send", response_model=TransactionResponse)
async def send_doge(
    request: SendRequest,
    wallet: Wallet = Depends(get_wallet)
):
    """Send DOGE to an address."""
    try:
        txid = await wallet.send(
            request.address,
            request.amount,
            request.comment or "",
            request.comment_to or ""
        )
        return TransactionResponse(
            txid=txid,
            amount=request.amount,
            address=request.address
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transaction failed: {e}")


@app.post("/address", response_model=AddressResponse)
async def create_address(
    label: Optional[str] = None,
    wallet: Wallet = Depends(get_wallet)
):
    """Create a new Dogecoin address."""
    try:
        address = await wallet.create_address(label or "")
        return AddressResponse(address=address, label=label)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create address: {e}")


@app.get("/blockchain-info")
async def get_blockchain_info(wallet: Wallet = Depends(get_wallet)):
    """Get blockchain information."""
    try:
        info = await wallet.client.getblockchaininfo()
        return {
            "blocks": info.blocks,
            "chain": info.chain,
            "difficulty": info.difficulty,
            "mediantime": info.mediantime
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get blockchain info: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)