from fastapi import APIRouter
from typing import List

from controller.crypto_manager import CryptoManager
from database.base_models.cryptocurrency_base import CryptoToken

router = APIRouter()

# Create a single instance of CryptoManager
crypto_manager = CryptoManager()

@router.get("/top-tokens", response_model=List[CryptoToken])
async def get_top_tokens():
    """Get list of supported tokens"""
    await crypto_manager.update_supported_currencies()
    return list(crypto_manager.supported_currencies.values())

@router.get("/transaction-details/{currency}/{amount}")
async def get_transaction_details(currency: str, amount: float):
    """Get transaction details for purchasing CABL tokens"""
    # Ensure currencies are up to date
    # await crypto_manager.update_supported_currencies()
    return await crypto_manager.get_transaction_details(currency, amount) 