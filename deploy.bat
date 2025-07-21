@echo off
REM Vercel Deployment Script for Windows

echo 🚀 Starting Vercel Deployment for Emergency Vehicle Detection
echo ==================================================

REM Step 1: Commit latest changes
echo 📦 Committing latest changes...
git add .
git commit -m "Deploy: Updated for Vercel deployment %date% %time%"

REM Step 2: Push to GitHub
echo ⬆️  Pushing to GitHub...
git push origin main

REM Step 3: Deploy to Vercel
echo 🚀 Deploying to Vercel...
vercel --prod

echo ✅ Deployment complete!
echo 🌐 Your app should be live at the URL shown above
pause
