# Vercel serverless function entry point - lightweight with external ML API
from lightweight_app import app

# This is the entry point for Vercel
# Export the app for Vercel's WSGI handler
handler = app
