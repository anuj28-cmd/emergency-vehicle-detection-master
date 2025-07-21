#!/bin/bash
# Vercel Deployment Script

echo "🚀 Starting Vercel Deployment for Emergency Vehicle Detection"
echo "=================================================="

# Step 1: Commit latest changes
echo "📦 Committing latest changes..."
git add .
git commit -m "Deploy: Updated for Vercel deployment $(date)"

# Step 2: Push to GitHub
echo "⬆️  Pushing to GitHub..."
git push origin main

# Step 3: Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your app should be live at the URL shown above"
