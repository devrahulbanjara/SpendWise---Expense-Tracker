from database import profiles_collection, transactions_collection, users_collection
from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId


async def get_active_profile(user_id: int):
    """Fetches the active profile for the user and converts ObjectId to string."""
    
    user = await users_collection.find_one({"user_id": user_id})
    if not user or "active_profile_id" not in user:
        raise HTTPException(status_code=404, detail="User or active profile not found")

    profile = await profiles_collection.find_one({"user_id": user_id, "profile_id": user["active_profile_id"]})
    if not profile:
        raise HTTPException(status_code=404, detail="Active profile not found")

    # Convert `_id` to string if present
    profile["_id"] = str(profile["_id"]) if "_id" in profile else None

    return profile


async def switch_profile(user_id: int, profile_id: int):
    """Switches the active profile for the user."""
    
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = await profiles_collection.find_one({"user_id": user_id, "profile_id": profile_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update the active profile
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"active_profile_id": profile_id}}
    )

    return {"message": f"Switched to profile {profile['profile_name']}", "profile_id": profile_id}



async def create_default_profile(user_id: int):
    """Creates a default profile and returns its ID."""
    default_profile = {
        "user_id": user_id,
        "profile_id": 1,
        "profile_name": "Personal",
        "profile_total_income": 0,
        "profile_total_expense": 0,
        "profile_total_balance": 0
    }
    await profiles_collection.insert_one(default_profile)
    return 1  # Default profile_id


async def update_income(user_id: int, amount: float):
    """Adds income to the active profile."""
    user = await users_collection.find_one({"user_id": user_id})
    profile = await get_active_profile(user_id)

    new_income = profile["profile_total_income"] + amount
    new_balance = profile["profile_total_balance"] + amount

    await profiles_collection.update_one(
        {"user_id": user_id, "profile_id": user["active_profile_id"]},
        {"$set": {"profile_total_income": new_income, "profile_total_balance": new_balance}}
    )

    return {"message": "Income updated successfully"}


async def add_expense(user_id: int, description: str, amount: float):
    """Adds an expense to the active profile."""
    user = await users_collection.find_one({"user_id": user_id})
    profile = await get_active_profile(user_id)

    new_expense = profile["profile_total_expense"] + amount
    new_balance = profile["profile_total_balance"] - amount

    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    await transactions_collection.insert_one({
        "user_id": user_id,
        "profile_id": user["active_profile_id"],
        "transaction_type": "expense",
        "transaction_description": description,
        "transaction_amount": amount,
        "timestamp": datetime.utcnow()
    })

    await profiles_collection.update_one(
        {"user_id": user_id, "profile_id": user["active_profile_id"]},
        {"$set": {"profile_total_expense": new_expense, "profile_total_balance": new_balance}}
    )

    return {"message": "Expense added successfully"}


async def create_profile(user_id: int, profile_name: str):
    """Creates a new profile for the user."""
    profile_count = await profiles_collection.count_documents({"user_id": user_id})
    new_profile_id = profile_count + 1

    await profiles_collection.insert_one({
        "user_id": user_id,
        "profile_id": new_profile_id,
        "profile_name": profile_name,
        "profile_total_income": 0,
        "profile_total_expense": 0,
        "profile_total_balance": 0,
    })

    return {"message": "Profile created successfully", "profile_id": new_profile_id}
