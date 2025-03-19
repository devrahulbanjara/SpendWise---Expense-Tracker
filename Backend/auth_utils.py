import bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId

# Connect to the MongoDB client
client = MongoClient("mongodb://localhost:27017/")  # Ensure MongoDB is running
db = client["user_database"]
collection = db["users"]

# Function to register a new user with currency preference
def register_user(email, password, full_name, currency_preference):
    # Check if email already exists
    existing_user = collection.find_one({"email": email})
    if existing_user:
        print("Email already registered")
        return

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Store the user in the database
    user_data = {
        "email": email,
        "password": hashed_password,
        "full_name": full_name,  # Full name is added
        "currency_preference": currency_preference  # New field for currency preference
    }

    collection.insert_one(user_data)
    print(f"User {full_name} registered successfully with currency preference {currency_preference}")

# Function to validate user during login
def validate_user(email, password):
    # Find the user by email
    user = collection.find_one({"email": email})
    if user:
        # Check if the password is correct
        if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            # Show currency preference if available
            currency_preference = user.get("currency_preference", "Not set")
            return f"Login successful. Welcome {user.get('full_name', 'User')}! Currency preference: {currency_preference}"
        else:
            return "Invalid password"
    else:
        return "Email not found"

# Example Usage
if __name__ == "__main__":
    # Register a user with currency preference
    register_user("adam@10smith.com", "mypassword", "Adam Smith", "Nrs")

    # Try to validate the user
    print(validate_user("adam@10smith.com", "mypassword"))  
    print(validate_user("adam@10smith.com", "wrongpassword"))  
    print(validate_user("nonexistent@example.com", "mypassword"))  