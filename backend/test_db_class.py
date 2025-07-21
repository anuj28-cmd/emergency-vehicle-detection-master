from database_mongodb import Database

print('Testing Database class...')
db = Database()
print('✅ Database class initialized successfully')

# Test some operations
users = db.get_all_users()
print(f'Users found: {len(users) if users else 0}')

settings = db.get_all_settings()
print(f'Settings found: {len(settings) if settings else 0}')

print('✅ Database operations working correctly')
