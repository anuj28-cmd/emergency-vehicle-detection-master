#!/usr/bin/env python3
"""
Database Connection Test Script
Tests both local and Atlas MongoDB connections
"""

import os
import sys
import pymongo
from dotenv import load_dotenv
from datetime import datetime

def test_database_connection():
    """Test the database connection"""
    print("=" * 50)
    print("DATABASE CONNECTION TEST")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB URI from environment
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/emergency_vehicle_detection')
    
    print(f"Testing connection...")
    print(f"URI type: {'MongoDB Atlas' if mongodb_uri.startswith('mongodb+srv://') else 'Local MongoDB'}")
    
    try:
        # Test basic pymongo functionality
        print(f"PyMongo version: {pymongo.version}")
        
        # Create client with timeout
        print("Creating MongoDB client...")
        client = pymongo.MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=10000,  # 10 second timeout
            connectTimeoutMS=20000,          # 20 second timeout  
            socketTimeoutMS=20000            # 20 second timeout
        )
        
        # Test connection with ping
        print("Testing connection with ping...")
        start_time = datetime.now()
        client.admin.command('ping')
        end_time = datetime.now()
        
        print(f"✅ MongoDB connection successful!")
        print(f"Response time: {(end_time - start_time).total_seconds():.2f} seconds")
        
        # Get database information
        db = client.get_database()
        print(f"Database name: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Test collection operations
        print("\nTesting collection operations...")
        users_collection = db.users
        
        # Count documents
        user_count = users_collection.count_documents({})
        print(f"Users in database: {user_count}")
        
        detections_collection = db.detections
        detection_count = detections_collection.count_documents({})
        print(f"Detections in database: {detection_count}")
        
        client.close()
        print("\n✅ All database tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database connection failed!")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Test fallback behavior
        print("\nTesting fallback behavior...")
        try:
            from database_mongodb import Database
            db_instance = Database()
            print("✅ Database fallback working (using in-memory storage)")
        except Exception as fallback_error:
            print(f"❌ Database fallback also failed: {fallback_error}")
        
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
