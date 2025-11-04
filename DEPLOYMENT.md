# Deployment Guide

Complete guide to deploy JournalX on Render.

## Prerequisites

- GitHub account (code already on GitHub)
- Email address
- Credit card (for verification, won't be charged on free tier)
- 15-20 minutes

## Step-by-Step Instructions

### Step 1: Sign Up

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

### Step 2: Create PostgreSQL Database

1. In Render dashboard, click "New +"
2. Select "PostgreSQL"
3. Configure:
   - **Name:** `journalx-db` (or any name)
   - **Database:** `journalx`
   - **User:** (auto-generated)
   - **Region:** Choose closest to you
   - **PostgreSQL Version:** Latest (14 or 15)
   - **Plan:** Free (for testing)
4. Click "Create Database"
5. Wait for database to be created (1-2 minutes)
6. **Important:** Copy the **Internal Database URL** - you'll need it

### Step 3: Create Web Service

1. Click "New +" → "Web Service"
2. Select "Build and deploy from a Git repository"
3. Connect your GitHub account if not already connected
4. Select repository: `Kiriagoray/Trading-Journal`
5. Configure:
   - **Name:** `journalx` (or any name)
   - **Region:** Same as database
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput`
   - **Start Command:** `gunicorn journal_project.wsgi`
   - **Environment:** Python 3
   - **Python Version:** 3.11

### Step 4: Configure Environment Variables

In the Web Service settings, go to **"Environment"** tab and add:

**SECRET_KEY**
Generate it using:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output and paste as the value.

**DEBUG**
Value: `False`

**ALLOWED_HOSTS**
Value: `journalx.onrender.com,yourdomain.com`

**DATABASE_URL**
Value: Paste the **Internal Database URL** from your PostgreSQL service

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

### Step 5: Deploy

1. Click "Create Web Service"
2. Render will start building automatically
3. Watch the build logs in real-time
4. Wait for "Your service is live" message (5-10 minutes)

### Step 6: Create Admin User

1. In Render dashboard, go to your Web Service
2. Click "Shell" tab (or use Render's shell)
3. Run:
```bash
python manage.py createsuperuser
```
4. Follow the prompts to create your admin account

### Step 7: Access Your Application

1. Render provides a URL: `https://journalx.onrender.com` (or your service name)
2. Your app is now live!

### Step 8: Custom Domain (Optional)

1. Go to "Settings" → "Custom Domains"
2. Add your domain name
3. Follow DNS configuration instructions

## Important Notes

### Free Tier Limitations

- **Sleeps after 15 minutes** of inactivity (free tier only)
- First request after sleep takes 30-60 seconds to wake up
- Upgrade to paid plan ($7/month) to avoid sleeping

### Database Backups

- Free tier: Manual backups only
- Paid plans: Automatic daily backups

### Static Files

- Automatically collected during build (included in build command)
- Served automatically by Render

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify Python version is 3.11
- Ensure all dependencies in requirements.txt are correct

### Database Connection Errors
- Verify PostgreSQL service is running
- Check that `DATABASE_URL` is set correctly
- Use the Internal Database URL from PostgreSQL service

### Static Files Not Loading
- Ensure `collectstatic` runs in build command
- Check build logs for static file collection messages

### Service Sleeps (Free Tier)
- This is normal on free tier
- First request after sleep will be slow (30-60 seconds)
- Consider upgrading to Starter plan ($7/month) to prevent sleeping

### 500 Errors
- Check deployment logs for specific error messages
- Verify `DEBUG=False` and `ALLOWED_HOSTS` is set
- Ensure migrations ran successfully (check build logs)

### Email Not Sending
- Verify all EMAIL_* environment variables are set
- Check Gmail app password is correct
- Review Render logs for email errors

## Post-Deployment Checklist

- [ ] Test user registration
- [ ] Test login/logout
- [ ] Create a test trade entry
- [ ] Test password reset functionality
- [ ] Verify all features work correctly
- [ ] Set up custom domain (optional)

## Cost

- **Free tier:** $0 (with limitations - sleeps after inactivity)
- **Starter plan:** $7/month (no sleep, better performance)
- **Database:** Free tier available

## Support

- Render Documentation: https://render.com/docs
- Check build/deployment logs for detailed error messages
- Render provides helpful error messages in the dashboard

---

Your JournalX application is now deployed and ready to use!
