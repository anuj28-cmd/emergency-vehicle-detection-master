# 🚀 Complete Vercel Deployment Guide

## Emergency Vehicle Detection System - Vercel Deployment

### Prerequisites ✅
- [x] GitHub repository exists
- [x] Vercel CLI installed
- [x] MongoDB Atlas database configured
- [x] Project files ready

---

## Step-by-Step Deployment Process

### 1. **Login to Vercel**
```bash
vercel login
```
- Follow the prompts to login with GitHub

### 2. **Initialize Vercel Project**
```bash
vercel
```
- Choose "Link to existing project" if you have one, or "Create new project"
- Select your GitHub repository
- Choose project settings:
  - **Framework**: Other
  - **Root Directory**: `./` (project root)
  - **Build Command**: Leave empty
  - **Output Directory**: Leave empty

### 3. **Configure Environment Variables**
In Vercel Dashboard (vercel.com):
1. Go to your project
2. Click "Settings" tab
3. Click "Environment Variables"
4. Add these variables:

```
MONGODB_URI = mongodb+srv://Admin:Admin123@evdetect.fhoj3tp.mongodb.net/emergency_vehicle_detection?retryWrites=true&w=majority&appName=EVDetect&readPreference=secondary&connectTimeoutMS=60000&socketTimeoutMS=60000&serverSelectionTimeoutMS=60000&maxPoolSize=10&minPoolSize=5

JWT_SECRET = ENWZ7e9zkFxl+88xHRaaq0tl4CaVEe9EmPVkQhTgTXg=

FLASK_ENV = production

DEBUG = False
```

### 4. **Deploy Backend and Frontend**

#### Backend Deployment:
```bash
cd backend
vercel --prod
```

#### Frontend Deployment:
```bash
cd frontend
vercel --prod
```

### 5. **Update Frontend API Configuration**
After backend deployment, update `frontend/src/config/api.js`:
```javascript
const API_BASE_URL = 'https://your-backend-url.vercel.app';
```

### 6. **Redeploy Frontend**
```bash
cd frontend
vercel --prod
```

---

## Project Structure for Vercel

```
emergency-vehicle-detection/
├── backend/
│   ├── index.py          # Entry point
│   ├── app.py           # Main Flask app
│   ├── vercel.json      # Vercel config
│   ├── requirements-vercel.txt
│   └── database_mongodb.py
├── frontend/
│   ├── package.json
│   ├── vercel.json      # Frontend config
│   └── src/
└── deploy.bat           # Windows deployment script
```

---

## Expected Deployment URLs

After successful deployment:
- **Backend API**: `https://your-backend-project.vercel.app`
- **Frontend App**: `https://your-frontend-project.vercel.app`

---

## Verification Steps

### 1. Test Backend API:
```bash
curl https://your-backend-url.vercel.app/api/health
```

### 2. Test Database Connection:
```bash
curl https://your-backend-url.vercel.app/api/test-db
```

### 3. Test Frontend:
- Open frontend URL in browser
- Try login/register functionality
- Test image upload feature

---

## Troubleshooting Common Issues

### Issue 1: Module Import Errors
**Solution**: Ensure all dependencies are in `requirements-vercel.txt`

### Issue 2: Database Connection Timeout
**Solution**: Check MongoDB Atlas network access (allow all IPs: 0.0.0.0/0)

### Issue 3: CORS Errors
**Solution**: Update CORS configuration in `app.py`:
```python
CORS(app, resources={r"/api/*": {"origins": ["https://your-frontend-url.vercel.app"]}})
```

### Issue 4: Environment Variables Not Working
**Solution**: 
1. Check spelling in Vercel dashboard
2. Redeploy after adding variables
3. Use `os.environ.get()` in code

---

## Security Considerations

### ⚠️ Important Security Updates for Production:

1. **Update MongoDB credentials** (current ones are exposed)
2. **Generate new JWT secret**
3. **Set specific CORS origins** (not wildcard *)
4. **Enable MongoDB IP whitelist**

### Recommended Security Updates:
```python
# In app.py - Update CORS for production
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-frontend-domain.vercel.app"]
    }
})

# Use environment-specific JWT secret
JWT_SECRET = os.environ.get('JWT_SECRET_PROD', 'fallback-secret')
```

---

## Monitoring and Maintenance

### Vercel Dashboard Features:
- **Analytics**: Monitor traffic and performance
- **Functions**: Check serverless function logs
- **Deployments**: View deployment history
- **Domains**: Configure custom domains

### MongoDB Atlas Monitoring:
- **Metrics**: Database performance
- **Alerts**: Set up monitoring alerts
- **Backup**: Configure automated backups

---

## Next Steps After Deployment

1. **Test all functionality** thoroughly
2. **Set up custom domain** (optional)
3. **Configure monitoring** and alerts
4. **Update security settings**
5. **Set up CI/CD pipeline** for automatic deployments

---

## Quick Deploy Commands

For future deployments, use these commands:

```bash
# Commit and push changes
git add .
git commit -m "Update: [description]"
git push origin main

# Deploy to Vercel
vercel --prod
```

Or use the provided script:
```bash
# Windows
deploy.bat

# Linux/Mac
./deploy.sh
```
