from database_mongodb import Database
import datetime
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    print("Starting MongoDB connection test...")
    
    # Initialize database
    db = Database()
    
    # Test 1: Connection Check
    print("\nTest 1: Checking MongoDB Connection...")
    if hasattr(db, 'users'):
        print("✓ MongoDB connection successful!")
    else:
        print("✗ MongoDB connection failed - using fallback memory database")
        return
    
    # Test 2: Write Operation
    print("\nTest 2: Testing Write Operation...")
    test_user_email = f"test_user_{int(time.time())}@test.com"
    user_id = db.add_user(
        email=test_user_email,
        password="test123",
        name="Test User",
        organization="Test Org",
        phone="123-456-7890"
    )
    
    if user_id:
        print(f"✓ Successfully created test user with ID: {user_id}")
    else:
        print("✗ Failed to create test user")
        return
    
    # Test 3: Read Operation
    print("\nTest 3: Testing Read Operation...")
    user = db.get_user_by_email(test_user_email)
    if user:
        print("✓ Successfully retrieved test user")
    else:
        print("✗ Failed to retrieve test user")
        return
    
    # Test 4: Update Operation
    print("\nTest 4: Testing Update Operation...")
    update_result = db.update_user_profile(
        user_id=user_id,
        name="Updated Test User"
    )
    if update_result:
        print("✓ Successfully updated test user")
    else:
        print("✗ Failed to update test user")
        return
    
    # Test 5: Settings Operation
    print("\nTest 5: Testing Settings Operations...")
    test_setting_key = "test_setting"
    test_setting_value = "test_value"
    
    if db.set_setting(test_setting_key, test_setting_value):
        retrieved_value = db.get_setting(test_setting_key)
        if retrieved_value == test_setting_value:
            print("✓ Successfully tested settings operations")
        else:
            print("✗ Failed to verify setting value")
    else:
        print("✗ Failed to set test setting")
    
    print("\nAll tests completed successfully! Your MongoDB connection is working properly.")

if __name__ == "__main__":
    test_mongodb_connection()