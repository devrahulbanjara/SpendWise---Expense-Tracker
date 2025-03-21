from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, profile
from routes.transactions import router as transactions_router 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(transactions_router)

@app.get("/")
def home():
    return {"message": "Welcome to AarthikNiti Expense Tracker API"}