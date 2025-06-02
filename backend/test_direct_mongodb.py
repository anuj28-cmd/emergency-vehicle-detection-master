import os
import time
from dotenv import load_dotenv
from pymongo import MongoClient
import traceback

# Load environment variables
load_dotenv()

def test_direct_connection():
    """Test connection to MongoDB Atlas using direct connection string"""
    connection_string = os.environ.get('MONGODB_URI')
    if not connection_string:
        print("ERROR: No MongoDB URI found in environment variables")
        return
    
    # Hide sensitive information when printing
    print_string = connection_string
    if '@' in print_string:
        parts = print_string.split('@')
        front_part = parts[0].split('://')
        if len(front_part) > 1:
            print_string = f"{front_part[0]}://***:***@{parts[1]}"
    
    print(f"Testing connection with: {print_string}")
    
    try:
        start_time = time.time()
        print("Attempting to connect...")
        client = MongoClient(connection_string)
        
        # Force a connection to check if it works
        print("Pinging database...")
        client.admin.command('ping')
        
        end_time = time.time()
        print(f"✅ Connected successfully in {end_time - start_time:.2f} seconds!")
        
        # Get database information
        print("\nCluster information:")
        print(f"Server info: {client.server_info()}")
        
        # List databases
        print("\nAvailable databases:")
        for db in client.list_database_names():
            print(f" - {db}")
        
        # Use the specified database
        db_name = connection_string.split('/')[-1].split('?')[0]
        if not db_name:
            db_name = "emergency_vehicle_detection"
        
        db = client[db_name]
        print(f"\nUsing database: {db_name}")
        
        # List collections
        print("Available collections:")
        for collection in db.list_collection_names():
            print(f" - {collection}")
            
        # Close connection
        client.close()
        print("\nConnection closed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        print("\nTroubleshooting tips:")
        print("1. Verify your IP address is whitelisted in MongoDB Atlas")
        print("2. Check if your network/firewall is blocking MongoDB connections")
        print("3. Ensure your MongoDB Atlas cluster is active (not paused)")
        print("4. Verify your username and password are correct")
        print("5. Try increasing timeout parameters in the connection string")

if __name__ == "__main__":
    test_direct_connection()
