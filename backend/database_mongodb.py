import os
import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
from bson.objectid import ObjectId
import urllib.parse
import time

class Database:
    def __init__(self):
        # Get MongoDB connection string from environment variable
        # For local development, use a local MongoDB or set this to a MongoDB Atlas connection string
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/emergency_vehicle_detection')
        
        # Connect to MongoDB
        try:
            print("Connecting to MongoDB...")
            # Use a timeout for the initial connection
            self.client = pymongo.MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout for server selection
                connectTimeoutMS=30000,         # 30 second timeout for connection
                socketTimeoutMS=30000,          # 30 second timeout for socket operations
                readPreference='secondaryPreferred'  # Allow reading from secondary nodes
            )
            
            # Test the connection
            self.client.admin.command('ping')
            print("MongoDB connection successful!")
            
            self.db = self.client.get_database()
            
            # Create collections if they don't exist
            self.users = self.db.users
            self.detections = self.db.detections
            self.settings = self.db.settings
            
            # Create indexes
            self.users.create_index('email', unique=True)
            self.detections.create_index('user_id')
            self.settings.create_index('key', unique=True)
            
            print("MongoDB setup complete.")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            # Fallback to in-memory storage for testing
            self._init_memory_db()
    
    def _init_memory_db(self):
        """Initialize in-memory database for testing/fallback"""
        print("Using in-memory database as fallback")
        self.memory_db = {
            'users': [
                {
                    'id': '1',
                    'email': 'admin@example.com',
                    'password': generate_password_hash('admin123'),
                    'name': 'Admin User',
                    'role': 'admin',
                    'organization': 'Emergency Services',
                    'phone': '123-456-7890',
                    'created_at': datetime.datetime.now().isoformat(),
                    'last_login': datetime.datetime.now().isoformat()
                },
                {
                    'id': '2',
                    'email': 'user@example.com',
                    'password': generate_password_hash('user123'),
                    'name': 'Regular User',
                    'role': 'user',
                    'organization': 'Traffic Department',
                    'phone': '987-654-3210',
                    'created_at': datetime.datetime.now().isoformat(),
                    'last_login': datetime.datetime.now().isoformat()
                }
            ],
            'detections': [],
            'settings': {
                'detection_threshold': '70',
                'notifications': 'true',
                'emergency_services': 'true',
                'traffic_system': 'true',
                'model_version': 'emergency_vehicle_model_final.h5'
            }
        }
    
    def add_user(self, email, password, name, organization=None, phone=None):
        """Add a new user to the database"""
        try:
            # Check if MongoDB is available
            if hasattr(self, 'users'):
                user_id = str(ObjectId())
                user = {
                    'id': user_id,
                    'email': email,
                    'password': generate_password_hash(password),
                    'name': name,
                    'role': 'user',  # Default role
                    'organization': organization,
                    'phone': phone,
                    'created_at': datetime.datetime.now().isoformat(),
                    'last_login': datetime.datetime.now().isoformat()
                }
                self.users.insert_one(user)
                return user_id
            else:
                # Fallback to in-memory
                user_id = str(len(self.memory_db['users']) + 1)
                user = {
                    'id': user_id,
                    'email': email,
                    'password': generate_password_hash(password),
                    'name': name,
                    'role': 'user',  # Default role
                    'organization': organization,
                    'phone': phone,
                    'created_at': datetime.datetime.now().isoformat(),
                    'last_login': datetime.datetime.now().isoformat()
                }
                self.memory_db['users'].append(user)
                return user_id
        except Exception as e:
            print(f"Error adding user: {e}")
            return None
    
    def get_user_by_email(self, email):
        """Get a user by email"""
        try:
            if hasattr(self, 'users'):
                user = self.users.find_one({'email': email})
                return user if user else None
            else:
                # Fallback to in-memory
                for user in self.memory_db['users']:
                    if user['email'] == email:
                        return user
                return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def verify_user(self, email, password):
        """Verify user credentials"""
        user = self.get_user_by_email(email)
        
        if user and check_password_hash(user['password'], password):
            # Update last login time
            if hasattr(self, 'users'):
                self.users.update_one(
                    {'email': email},
                    {'$set': {'last_login': datetime.datetime.now().isoformat()}}
                )
            else:
                # Fallback to in-memory
                for i, u in enumerate(self.memory_db['users']):
                    if u['email'] == email:
                        self.memory_db['users'][i]['last_login'] = datetime.datetime.now().isoformat()
            
            return user
        
        return None
    
    def update_user_profile(self, user_id, name=None, organization=None, phone=None):
        """Update user profile"""
        try:
            update_data = {}
            if name:
                update_data['name'] = name
            if organization:
                update_data['organization'] = organization
            if phone:
                update_data['phone'] = phone
            
            if hasattr(self, 'users'):
                result = self.users.update_one(
                    {'id': user_id},
                    {'$set': update_data}
                )
                return result.modified_count > 0
            else:
                # Fallback to in-memory
                for i, user in enumerate(self.memory_db['users']):
                    if user['id'] == user_id:
                        for key, value in update_data.items():
                            self.memory_db['users'][i][key] = value
                        return True
                return False
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    def change_password(self, user_id, new_password):
        """Change user password"""
        try:
            hashed_password = generate_password_hash(new_password)
            
            if hasattr(self, 'users'):
                result = self.users.update_one(
                    {'id': user_id},
                    {'$set': {'password': hashed_password}}
                )
                return result.modified_count > 0
            else:
                # Fallback to in-memory
                for i, user in enumerate(self.memory_db['users']):
                    if user['id'] == user_id:
                        self.memory_db['users'][i]['password'] = hashed_password
                        return True
                return False
        except Exception as e:
            print(f"Error changing password: {e}")
            return False
    
    def add_detection(self, detection_data, user_id):
        """Add a new detection to the database"""
        try:
            detection_data['user_id'] = user_id
            
            if hasattr(self, 'detections'):
                self.detections.insert_one(detection_data)
                return True
            else:
                # Fallback to in-memory
                self.memory_db['detections'].append(detection_data)
                return True
        except Exception as e:
            print(f"Error adding detection: {e}")
            return False
    
    def get_detections(self, limit=100, user_id=None):
        """Get detection history"""
        try:
            if hasattr(self, 'detections'):
                query = {'user_id': user_id} if user_id else {}
                detections = list(self.detections.find(query).sort('timestamp', -1).limit(limit))
                
                # Convert ObjectId to string
                for detection in detections:
                    if '_id' in detection:
                        detection['_id'] = str(detection['_id'])
                
                return detections
            else:
                # Fallback to in-memory
                detections = self.memory_db['detections']
                if user_id:
                    detections = [d for d in detections if d['user_id'] == user_id]
                detections = sorted(detections, key=lambda d: d['timestamp'], reverse=True)[:limit]
                return detections
        except Exception as e:
            print(f"Error getting detections: {e}")
            return []
    
    def get_detection_stats(self):
        """Get detection statistics"""
        try:
            # Initialize stats
            stats = {
                'detection_types': {},
                'by_month': {},
                'avg_confidence': 0
            }
            
            detections = []
            if hasattr(self, 'detections'):
                detections = list(self.detections.find())
            else:
                # Fallback to in-memory
                detections = self.memory_db['detections']
            
            if not detections:
                return stats
            
            # Process detections
            total_confidence = 0
            detection_count = len(detections)
            
            for detection in detections:
                # Count by detection type
                detection_type = detection.get('detection_type', 'Unknown')
                if detection_type in stats['detection_types']:
                    stats['detection_types'][detection_type] += 1
                else:
                    stats['detection_types'][detection_type] = 1
                
                # Add to total confidence
                total_confidence += detection.get('confidence', 0)
                
                # Process by month
                try:
                    timestamp = detection.get('timestamp')
                    if timestamp:
                        date = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        month = date.strftime('%Y-%m')
                        
                        if month not in stats['by_month']:
                            stats['by_month'][month] = {}
                        
                        if detection_type in stats['by_month'][month]:
                            stats['by_month'][month][detection_type] += 1
                        else:
                            stats['by_month'][month][detection_type] = 1
                except Exception as e:
                    print(f"Error processing date: {e}")
            
            # Calculate average confidence
            stats['avg_confidence'] = total_confidence / detection_count if detection_count > 0 else 0
            
            return stats
        except Exception as e:
            print(f"Error getting detection stats: {e}")
            return {
                'detection_types': {},
                'by_month': {},
                'avg_confidence': 0
            }
    
    def get_setting(self, key):
        """Get a setting value"""
        try:
            if hasattr(self, 'settings'):
                setting = self.settings.find_one({'key': key})
                return setting['value'] if setting else None
            else:
                # Fallback to in-memory
                return self.memory_db['settings'].get(key)
        except Exception as e:
            print(f"Error getting setting: {e}")
            return None
    
    def set_setting(self, key, value):
        """Set a setting value"""
        try:
            if hasattr(self, 'settings'):
                self.settings.update_one(
                    {'key': key},
                    {'$set': {'value': value}},
                    upsert=True
                )
                return True
            else:
                # Fallback to in-memory
                self.memory_db['settings'][key] = value
                return True
        except Exception as e:
            print(f"Error setting setting: {e}")
            return False
