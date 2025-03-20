from fastapi import FastAPI
from routes.auth import router as auth_router  # Import the router from your auth module
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],  # Change this to your frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the auth router (this will handle routes related to authentication)
app.include_router(auth_router)  # Include the auth router to enable login/signup routes

@app.get("/")
def home():
    return {"message": "Welcome to AarthikNiti Expense Tracker API"}