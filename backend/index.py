# Vercel serverless function entry point - database connection test
from db_test_app import app

# This is the entry point for Vercel
# Export the app for Vercel's WSGI handler
handler = app
