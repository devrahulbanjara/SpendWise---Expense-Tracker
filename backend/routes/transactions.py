from fastapi import APIRouter, HTTPException
from database import transactions_collection  # Ensure this is an async collection
from pydantic import BaseModel
from typing import List
from datetime import datetime
from bson import ObjectId 

# Initialize Router
router = APIRouter()

class Transaction(BaseModel):
    transaction_id: str
    transaction_type: str
    transaction_description: str
    transaction_amount: float
    timestamp: datetime

    # Override the Pydantic model's json method to handle ObjectId serialization
    class Config:
        # This ensures that ObjectId is converted to a string automatically
        json_encoders = {
            ObjectId: str
        }

@router.get("/transactions/top", response_model=List[Transaction])
async def get_top_transactions(user_id: str, profile_id: int):
    """Fetch the top 10 latest transactions for a given user and profile."""
    try:
        transactions_cursor = transactions_collection.find(
            {"user_id": user_id, "profile_id": profile_id}
        ).sort("timestamp", -1).limit(10)
        
        transactions = await transactions_cursor.to_list(length=10)  # Convert cursor to async list

        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")

        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))