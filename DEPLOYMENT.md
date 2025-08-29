# 🚀 AI Test Generator - Deployment Guide

This guide will help you deploy your AI Test Generator to production.

## 📋 Prerequisites

- [GitHub](https://github.com) account
- [Vercel](https://vercel.com) account (free)
- [Railway](https://railway.app) account (free) or [Heroku](https://heroku.com) account
- [Groq](https://groq.com) API key for AI quiz generation

## 🎯 Deployment Strategy

- **Frontend (React)**: Vercel (free, fast, easy)
- **Backend (FastAPI)**: Railway/Heroku (free tier available)
- **Database**: PostgreSQL (provided by Railway/Heroku)

## 🚀 Step 1: Deploy Backend to Railway

### 1.1 Prepare Your Repository
```bash
# Ensure your backend code is committed to GitHub
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

### 1.2 Deploy to Railway
1. Go to [Railway.app](https://railway.app) and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ENVIRONMENT=production
   ```
5. Railway will automatically detect Python and deploy your app
6. Note your app URL (e.g., `https://your-app.railway.app`)

### 1.3 Set Up Database
1. In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. Connect it to your app
3. Railway will automatically set the `DATABASE_URL` environment variable

### 1.4 Run Database Migrations
```bash
# In Railway dashboard, go to your app → "Deployments" → "Latest" → "View Logs"
# Add this command to your deployment:
alembic upgrade head
```

## 🌐 Step 2: Deploy Frontend to Vercel

### 2.1 Prepare Frontend
1. Update the API URL in your frontend code:
   ```typescript
   // In client/src/App.tsx and QuizHistoryPage.tsx
   const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';
   ```

2. Create a `.env.production` file in the client directory:
   ```bash
   VITE_API_URL=https://your-backend-url.railway.app
   ```

### 2.2 Deploy to Vercel
1. Go to [Vercel.com](https://vercel.com) and sign in with GitHub
2. Click "New Project" → "Import Git Repository"
3. Select your repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `client`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variable:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```
6. Click "Deploy"

## 🔧 Step 3: Configure CORS

### 3.1 Update Backend CORS
In `backend/app/config.py`, update the allowed origins:
```python
ALLOWED_ORIGINS: List[str] = [
    "https://your-frontend-domain.vercel.app",  # Your Vercel domain
    "http://localhost:3000",  # Keep for local development
    "http://localhost:5173",  # Keep for local development
]
```

### 3.2 Redeploy Backend
After updating CORS, redeploy your backend to Railway.

## 🧪 Step 4: Test Your Deployment

1. **Test Backend**: Visit `https://your-backend-url.railway.app/health`
2. **Test Frontend**: Visit your Vercel domain
3. **Test Full Flow**: Generate a quiz, submit answers, check history

## 🔑 Environment Variables Reference

### Backend (Railway)
```
GROQ_API_KEY=your_groq_api_key
ENVIRONMENT=production
DATABASE_URL=postgresql://... (auto-set by Railway)
PORT=3000 (auto-set by Railway)
```

### Frontend (Vercel)
```
VITE_API_URL=https://your-backend-url.railway.app
```

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure your backend CORS settings include your frontend domain
2. **Database Connection**: Check that `DATABASE_URL` is set correctly in Railway
3. **API Key**: Verify `GROQ_API_KEY` is set in Railway environment variables
4. **Build Errors**: Check Vercel build logs for any missing dependencies

### Debug Commands
```bash
# Check backend logs
railway logs

# Check frontend build logs
# View in Vercel dashboard → Deployments → Latest

# Test backend locally
cd backend
python main.py
```

## 💰 Cost Breakdown

- **Vercel**: Free tier (unlimited deployments, 100GB bandwidth)
- **Railway**: Free tier ($5 credit monthly, enough for small apps)
- **Database**: Included with Railway free tier
- **Total**: $0-5/month

## 🔄 Continuous Deployment

Both Vercel and Railway will automatically redeploy when you push to your main branch.

## 📱 Custom Domain (Optional)

### Vercel
1. Go to your project settings
2. Click "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### Railway
1. Go to your project settings
2. Click "Custom Domains"
3. Add your domain
4. Update CORS settings to include your domain

## 🎉 You're Live!

Your AI Test Generator is now hosted and accessible worldwide! 

- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-app.railway.app`
- **API Docs**: `https://your-app.railway.app/docs`

## 📞 Support

If you encounter issues:
1. Check the logs in both Vercel and Railway dashboards
2. Verify all environment variables are set correctly
3. Ensure CORS settings include your frontend domain
4. Check that your Groq API key is valid and has credits
