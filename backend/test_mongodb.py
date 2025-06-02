import os
import traceback
from dotenv import load_dotenv
from database_mongodb import Database

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test connection to MongoDB Atlas"""
    print("Testing MongoDB connection...")
    print(f"Connection string (obscured): {obscure_connection_string(os.environ.get('MONGODB_URI', 'Not set'))}")
    
    try:
        db = Database()
        
        # Check if we're using MongoDB or fallback
        if hasattr(db, 'users'):
            print("✅ Successfully connected to MongoDB!")
            
            # Test basic operations
            test_email = "test@example.com"
            
            # Clean up any previous test data
            existing_user = db.get_user_by_email(test_email)
            if existing_user:
                print(f"Found existing test user: {existing_user['name']}")
            
            # Test adding a user
            user_id = db.add_user(
                email=test_email,
                password="test123",
                name="Test User",
                organization="Test Org",
                phone="123-456-7890"
            )
            
            if user_id:
                print(f"✅ Successfully added test user with ID: {user_id}")
                
                # Test retrieving a user
                user = db.get_user_by_email(test_email)
                if user:
                    print(f"✅ Successfully retrieved user: {user['name']}")
                else:
                    print("❌ Failed to retrieve user")
                
                # Test user verification
                verified_user = db.verify_user(test_email, "test123")
                if verified_user:
                    print("✅ Successfully verified user credentials")
                else:
                    print("❌ Failed to verify user credentials")
            else:
                print("❌ Failed to add test user")
        else:
            print("⚠️ Using in-memory database fallback")
            print("Check your MongoDB connection string in the .env file")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        traceback.print_exc()
        print("\nMake sure you've replaced the placeholder MongoDB connection string in your .env file")
        print("The connection string should look like: mongodb+srv://username:password@cluster.mongodb.net/dbname")

def obscure_connection_string(conn_str):
    """Obscure sensitive parts of the connection string for safe printing"""
    if not conn_str or conn_str == 'Not set':
        return conn_str
    
    try:
        # Hide username and password
        parts = conn_str.split('@')
        if len(parts) > 1:
            auth_part = parts[0].split('://')
            if len(auth_part) > 1:
                return f"{auth_part[0]}://***:***@{parts[1]}"
        
        # If parsing fails, just return placeholder
        return "mongodb+srv://***:***@***.mongodb.net/***"
    except:
        return "Error parsing connection string"

if __name__ == "__main__":
    test_mongodb_connection()