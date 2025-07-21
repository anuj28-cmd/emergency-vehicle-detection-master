# Vercel serverless function entry point - with actual ML model
from model_app import app

# This is the entry point for Vercel
# Export the app for Vercel's WSGI handler
handler = app
