# Render Deployment Guide for JournalX

Render is another excellent option for deploying JournalX with a free tier.

## Prerequisites

- GitHub account
- Email address
- Credit card (for verification, won't be charged on free tier)
- 15-20 minutes

## Step-by-Step Deployment

### Step 1: Sign Up for Render

1. Go to [https://render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with your GitHub account
4. Authorize Render to access your repositories

### Step 2: Create PostgreSQL Database

1. In Render dashboard, click **"New +"**
2. Select **"PostgreSQL"**
3. Configure:
   - **Name:** `journalx-db` (or any name)
   - **Database:** `journalx`
   - **User:** (auto-generated)
   - **Region:** Choose closest to you
   - **PostgreSQL Version:** Latest (14 or 15)
   - **Plan:** Free (for testing)
4. Click **"Create Database"**
5. **Important:** Copy the **Internal Database URL** (you'll need it)

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Select **"Build and deploy from a Git repository"**
3. Connect your GitHub account if not already connected
4. Select repository: `Kiriagoray/Trading-Journal`
5. Configure:
   - **Name:** `journalx` (or any name)
   - **Region:** Same as database
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn journal_project.wsgi`
6. Click **"Advanced"** and add:
   - **Environment:** Python 3
   - **Python Version:** 3.11

### Step 4: Configure Environment Variables

In the Web Service settings, go to **"Environment"** tab and add:

```bash
# Security
SECRET_KEY=<generate-secret-key>
DEBUG=False
ALLOWED_HOSTS=journalx.onrender.com,yourdomain.com

# Database
USE_POSTGRESQL=True
DB_NAME=journalx
DB_USER=<from-postgres-service>
DB_PASSWORD=<from-postgres-service>
DB_HOST=<from-postgres-service>
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=teamjournalx@gmail.com
EMAIL_HOST_PASSWORD=bvbkonsxbzzcvcwf
DEFAULT_FROM_EMAIL=teamjournalx@gmail.com
```

**Getting Database Variables:**
- Go to your PostgreSQL service
- Copy the **Internal Database URL**
- Or use individual values from the service info

### Step 5: Add Build Script

Create a file `build.sh` in project root:

```bash
#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput
```

Then update **Build Command** in Render to:
```bash
chmod +x build.sh && ./build.sh
```

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will start building
3. Watch the build logs
4. Wait for "Your service is live" message

### Step 7: Create Superuser

1. In Render dashboard, go to your service
2. Click **"Shell"** tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts to create admin user

### Step 8: Access Your Application

1. Render provides a URL: `https://journalx.onrender.com`
2. Your app is live!

### Step 9: Custom Domain (Optional)

1. Go to **"Settings"** → **"Custom Domains"**
2. Add your domain
3. Follow DNS configuration instructions

## Important Notes

### Free Tier Limitations

- **Sleeps after 15 minutes** of inactivity (free tier)
- First request after sleep takes 30-60 seconds
- Upgrade to paid plan to avoid sleeping

### Database Backups

- Free tier: Manual backups
- Paid plans: Automatic daily backups

### Static Files

- Render automatically serves static files after `collectstatic`
- No additional configuration needed

## Troubleshooting

### Build Fails
- Check build logs
- Verify Python version
- Ensure all dependencies in requirements.txt

### Database Connection
- Verify PostgreSQL is running
- Check environment variables
- Use Internal Database URL for connection

### Static Files Not Loading
- Ensure `collectstatic` runs in build script
- Check STATIC_ROOT in settings.py

### Service Sleeps (Free Tier)
- This is normal on free tier
- First request after sleep will be slow
- Consider upgrading to prevent sleeping

## Cost Estimate

- **Free tier:** $0 (with limitations)
- **Starter plan:** $7/month (no sleep, better performance)
- **Database:** Free tier available

## Next Steps

1. Test all features
2. Set up monitoring
3. Configure custom domain
4. Consider upgrading if you need no-sleep service

---

**Ready?** Follow these steps for Render deployment!

