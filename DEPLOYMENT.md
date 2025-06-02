# Deployment Guide for Emergency Vehicle Detection System

This guide explains how to deploy the Emergency Vehicle Detection system on Vercel.

## Prerequisites

1. [Vercel Account](https://vercel.com/signup) - Sign up or login to Vercel
2. [MongoDB Atlas Account](https://www.mongodb.com/cloud/atlas/register) - For the database
3. [GitHub Account](https://github.com/join) - For storing your code repository

## Step 1: Set Up MongoDB Atlas

1. Create a free MongoDB Atlas cluster
2. Create a database named `emergency_vehicle_detection`
3. Create a database user with read/write access
4. Get your MongoDB connection string (it will look like: `mongodb+srv://username:password@cluster.mongodb.net/emergency_vehicle_detection?retryWrites=true&w=majority`)
5. Replace the placeholder in the backend's `.env` file with your actual connection string

## Step 2: Deploy the Backend

1. Push your code to GitHub
   ```bash
   cd c:\Users\heyan\OneDrive\Desktop\emergency-vehicle-detection-master
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/emergency-vehicle-detection.git
   git push -u origin main
   ```

2. Import your GitHub repository to Vercel:
   - Go to https://vercel.com/new
   - Select your GitHub repository
   - For the backend deployment:
     - Navigate to the backend directory in the import flow
     - Add the following environment variables:
       - `MONGODB_URI`: Your MongoDB Atlas connection string
       - `JWT_SECRET`: A secure random string for JWT token signing
     - Click Deploy

3. Note the URL of your deployed backend API (e.g., `https://emergency-vehicle-detection-backend.vercel.app`)

## Step 3: Deploy the Frontend

1. Update the frontend's .env file with your backend URL:
   ```
   REACT_APP_API_URL=https://emergency-vehicle-detection-backend.vercel.app
   ```

2. Deploy the frontend to Vercel:
   - Go to https://vercel.com/new again
   - Select the same GitHub repository
   - For the frontend deployment:
     - Navigate to the frontend directory in the import flow
     - Add the following environment variables:
       - `REACT_APP_API_URL`: Your backend API URL
     - Click Deploy

3. Note the URL of your deployed frontend (e.g., `https://emergency-vehicle-detection.vercel.app`)

## Step 4: Test the Deployment

1. Open your frontend URL in a browser
2. Register a new user or log in with the default credentials:
   - Email: admin@example.com
   - Password: admin123
3. Test the vehicle detection functionality by uploading images or using the webcam

## Troubleshooting

If you encounter issues:

1. Check the Vercel deployment logs for errors
2. Verify that your MongoDB Atlas connection string is correct
3. Ensure your environment variables are set correctly
4. Check CORS settings if the frontend cannot communicate with the backend

## Congratulations!

Your Emergency Vehicle Detection system is now deployed and accessible from anywhere!
