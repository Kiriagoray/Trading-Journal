# Deployment Guide

Complete guide to deploy JournalX on Railway.

## Prerequisites

- GitHub account (code already on GitHub)
- Email address  
- 10-15 minutes

## Step-by-Step Instructions

### Step 1: Sign Up

1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub (recommended)
4. Authorize Railway to access your repositories

### Step 2: Create Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Find and select: `Kiriagoray/Trading-Journal`
4. Railway will automatically detect it's a Django project

### Step 3: Add PostgreSQL Database

1. In project dashboard, click "+ New"
2. Select "Database" → "Add PostgreSQL"
3. Wait for database to be created (30 seconds)
4. Railway automatically links the database to your web service

**Note:** Railway automatically sets `DATABASE_URL` - no manual configuration needed.

### Step 4: Configure Environment Variables

1. Click on your **Web Service** (the Django service)
2. Go to the **"Variables"** tab
3. Verify `DATABASE_URL` is already there (added automatically)
4. Click "+ New Variable" and add these variables:

**SECRET_KEY**
Generate it using:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output and paste as the value.

**DEBUG**
Value: `False`

**ALLOWED_HOSTS**
Value: `*.railway.app`

**EMAIL_BACKEND**
Value: `django.core.mail.backends.smtp.EmailBackend`

**EMAIL_HOST**
Value: `smtp.gmail.com`

**EMAIL_PORT**
Value: `587`

**EMAIL_USE_TLS**
Value: `True`

**EMAIL_HOST_USER**
Value: `teamjournalx@gmail.com`

**EMAIL_HOST_PASSWORD**
Value: `bvbkonsxbzzcvcwf`

**DEFAULT_FROM_EMAIL**
Value: `teamjournalx@gmail.com`

### Step 5: Configure Start Command

1. In your Web Service, go to **"Settings"** tab
2. Find **"Start Command"**
3. Set it to:
```
python manage.py migrate && gunicorn journal_project.wsgi --bind 0.0.0.0:$PORT
```

### Step 6: Deploy

1. Railway will automatically start building and deploying
2. Watch the **"Deployments"** tab for progress
3. Wait for **"Active"** status (green checkmark)
4. Your app URL will be available in **"Settings"** → **"Domains"**

### Step 7: Create Admin User

1. In Railway dashboard, go to your Web Service
2. Click **"Deployments"** tab
3. Click on the latest deployment
4. Use the **"Logs"** tab or Railway's shell to run:
```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 8: Access Your Application

1. Railway provides a URL like: `https://your-app-name.railway.app`
2. Click the URL or find it in **"Settings"** → **"Domains"**
3. Your app is now live!

### Step 9: Custom Domain (Optional)

1. Go to **"Settings"** → **"Domains"**
2. Click **"Custom Domain"**
3. Add your domain name
4. Follow Railway's DNS configuration instructions

## Troubleshooting

### Build Fails
- Check build logs in "Deployments" tab
- Verify `requirements.txt` is correct
- Ensure Python version is compatible

### Database Connection Errors
- Verify PostgreSQL service is running
- Check that `DATABASE_URL` exists in Variables tab
- Railway auto-links databases - should work automatically

### Static Files Not Loading
- Static files are collected during build automatically
- If issues persist, check build logs

### 500 Errors
- Check deployment logs for specific error messages
- Verify `DEBUG=False` and `ALLOWED_HOSTS` is set
- Ensure migrations ran successfully (check logs)

### Email Not Sending
- Verify all EMAIL_* environment variables are set
- Check Gmail app password is correct
- Review Railway logs for email errors

## Post-Deployment Checklist

- [ ] Test user registration
- [ ] Test login/logout
- [ ] Create a test trade entry
- [ ] Test password reset functionality
- [ ] Verify all features work correctly
- [ ] Set up custom domain (optional)

## Cost

- Free tier: $5 credit/month (usually enough for testing)
- After free tier: ~$5-10/month for small traffic
- Database: Included in free tier

## Support

- Railway Documentation: https://docs.railway.app
- Check build/deployment logs for detailed error messages
- Railway automatically handles most configuration

---

Your JournalX application is now deployed and ready to use!
