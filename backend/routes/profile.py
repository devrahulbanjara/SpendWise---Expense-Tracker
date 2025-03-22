from fastapi import APIRouter, Depends
from core.config import get_current_user
from services.profile_service import (
    get_active_profile, update_income, add_expense, create_profile, switch_profile
)
from pydantic import BaseModel

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/dashboard")
async def dashboard(user: dict = Depends(get_current_user)):
    """Fetches details of the user's active profile."""
    return await get_active_profile(user["user_id"])


class IncomeUpdateRequest(BaseModel):
    amount: float


@router.post("/update_income")
async def update_income_endpoint(request: IncomeUpdateRequest, user: dict = Depends(get_current_user)):
    """Updates income for the active profile."""
    return await update_income(user["user_id"], request.amount)


class AddExpenseRequest(BaseModel):
    description: str
    amount: float


@router.post("/add_expense")
async def add_expense_endpoint(request: AddExpenseRequest, user: dict = Depends(get_current_user)):
    """Adds an expense for the active profile."""
    return await add_expense(user["user_id"], request.description, request.amount)


class ProfileCreateRequest(BaseModel):
    profile_name: str


@router.post("/create")
async def create_profile_endpoint(request: ProfileCreateRequest, user: dict = Depends(get_current_user)):
    """Creates a new profile."""
    return await create_profile(user["user_id"], request.profile_name)


class ProfileSwitchRequest(BaseModel):
    profile_id: int


@router.post("/switch")
async def switch_profile_endpoint(request: ProfileSwitchRequest, user: dict = Depends(get_current_user)):
    """Switches to another profile."""
    return await switch_profile(user["user_id"], request.profile_id)


async def get_recent_transactions(user_id: int, limit: int = 10):
    """Fetches the latest transactions for the active profile."""
    
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    active_profile_id = user.get("active_profile_id")
    if not active_profile_id:
        raise HTTPException(status_code=404, detail="No active profile found")

    transactions = await transactions_collection.find(
        {"user_id": user_id, "profile_id": active_profile_id}
    ).sort("timestamp", -1).limit(limit).to_list(length=limit)

    # Convert `_id` to string for JSON compatibility
    for transaction in transactions:
        transaction["_id"] = str(transaction["_id"])

    return transactions


@router.get("/recent_transactions")
async def recent_transactions(user: dict = Depends(get_current_user)):
    """Fetches the top 10 recent transactions for the active profile."""
    return await get_recent_transactions(user["user_id"])
