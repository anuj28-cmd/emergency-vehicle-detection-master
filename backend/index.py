# Vercel serverless function entry point - using simple app for testing
from simple_app import app

# This is the entry point for Vercel
# Export the app for Vercel's WSGI handler
handler = app
