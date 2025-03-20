import os
from fastapi import APIRouter, HTTPException, Depends
from database import users_collection
from models.user import SignupRequest, LoginRequest, UserResponse
from core.security import hash_password, verify_password, create_jwt_token
from core.config import get_current_user
from datetime import timedelta
from bson import ObjectId
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

# Initialize Google OAuth
oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    client_kwargs={"scope": "openid email profile"},
)

# ---------------------- Email & Password Authentication ----------------------

@router.post("/signup", response_model=UserResponse)
async def signup(user: SignupRequest):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    
    new_user = {
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed_password,
        "currency_preference": user.currency_preference,
        "auth_provider": "email"  # Track how the user signed up
    }
    await users_collection.insert_one(new_user)

    return UserResponse(**new_user)

@router.post("/login")
async def login(user: LoginRequest):
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token({"user_id": str(db_user["_id"]), "email": db_user["email"]}, expires_delta=timedelta(hours=1))
    
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_user_data(user: dict = Depends(get_current_user)):
    db_user = await users_collection.find_one({"_id": ObjectId(user["user_id"])}, {"_id": 0, "password": 0})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# ---------------------- Google OAuth Authentication ----------------------

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    if not user_info:
        raise HTTPException(status_code=400, detail="Google authentication failed")

    # Check if user exists in the database
    db_user = await users_collection.find_one({"email": user_info["email"]})

    if not db_user:
        # Create a new user if not exists
        new_user = {
            "full_name": user_info["name"],
            "email": user_info["email"],
            "password": None,  # No password required for Google sign-in
            "currency_preference": "USD",  # Set default currency or customize later
            "auth_provider": "google"
        }
        await users_collection.insert_one(new_user)
        db_user = new_user

    # Generate JWT token
    token = create_jwt_token({"user_id": str(db_user["_id"]), "email": db_user["email"]}, expires_delta=timedelta(hours=1))

    return RedirectResponse(url=f"http://localhost:5173/dashboard?token={token}")