# Vercel serverless function entry point
from app import app

# This is needed for Vercel's serverless function handler
handler = app
