# Vercel serverless function entry point
from app import app

# This is the entry point for Vercel
# Export the app for Vercel's WSGI handler
handler = app
