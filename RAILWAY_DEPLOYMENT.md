# Railway Deployment Guide for JournalX

Railway is the easiest platform to deploy JournalX. This guide will walk you through the entire process.

## Prerequisites

- GitHub account (your code is already there)
- Email address
- 10-15 minutes

## Step-by-Step Deployment

### Step 1: Sign Up for Railway

1. Go to [https://railway.app](https://railway.app)
2. Click **"Start a New Project"** or **"Login"**
3. Sign up with your GitHub account (recommended for easy integration)
4. Authorize Railway to access your GitHub repositories

### Step 2: Create a New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select your repository: `Kiriagoray/Trading-Journal`
4. Railway will automatically detect it's a Django project

### Step 3: Add PostgreSQL Database

1. In your project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a PostgreSQL database
4. **Important:** Note the connection details (you'll need them)

### Step 4: Link PostgreSQL to Web Service

1. In your project dashboard, you should see both services (PostgreSQL and Web)
2. Click on your **Web Service**
3. Go to **"Variables"** tab
4. Railway should automatically add `DATABASE_URL` - **verify it's there!**
5. If not, click **"+ New Variable"** and Railway will show you the database connection variables

**Note:** Our app automatically detects `DATABASE_URL`, so you don't need to set individual DB variables!

### Step 5: Configure Environment Variables

1. Still in **"Variables"** tab of your Web Service
2. Click **"+ New Variable"**
3. Add these variables:

```bash
# Security
SECRET_KEY=<generate-using-command-below>
DEBUG=False
ALLOWED_HOSTS=*.railway.app,yourdomain.com

# Email (use your Gmail credentials)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=teamjournalx@gmail.com
EMAIL_HOST_PASSWORD=bvbkonsxbzzcvcwf
DEFAULT_FROM_EMAIL=teamjournalx@gmail.com
```

**Note:** `DATABASE_URL` is automatically added by Railway when you link PostgreSQL - no need to set it manually!

**To generate SECRET_KEY:**
Run this command locally:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or use this online tool: https://djecrety.ir/

### Step 6: Configure Build and Start Commands

Railway usually auto-detects Django, but verify:

1. In your service settings, check **"Settings"** tab
2. **Build Command:** (leave empty or `pip install -r requirements.txt`)
3. **Start Command:** `python manage.py migrate && gunicorn journal_project.wsgi`

If gunicorn isn't in requirements, we'll add it.

### Step 7: Deploy

1. Railway will automatically start building and deploying
2. Watch the build logs - you should see:
   - Installing dependencies
   - Running migrations (if configured)
   - Starting the server
3. Wait for "Deployed successfully" message

### Step 8: Run Migrations

1. Go to your service dashboard
2. Click on the **"Deployments"** tab
3. Click on the latest deployment
4. Open the **"Logs"** tab
5. Or use Railway's CLI (if installed):
   ```bash
   railway run python manage.py migrate
   ```

Alternatively, you can add migrations to the start command:
```bash
python manage.py migrate && gunicorn journal_project.wsgi --bind 0.0.0.0:$PORT
```

### Step 9: Create Superuser

1. In Railway dashboard, go to your service
2. Click **"Variables"** → Look for **"Deploy Command"** or use **"Shell"**
3. Or use Railway CLI:
   ```bash
   railway run python manage.py createsuperuser
   ```

### Step 10: Access Your Application

1. Railway will provide a URL like: `https://your-app-name.railway.app`
2. Click on the URL or find it in the **"Settings"** → **"Domains"**
3. Your app should be live!

### Step 11: Custom Domain (Optional)

1. Go to **"Settings"** → **"Domains"**
2. Click **"Custom Domain"**
3. Add your domain name
4. Follow Railway's DNS instructions

## Updating Requirements.txt

We need to add `gunicorn` for production. I'll update requirements.txt now.

## Troubleshooting

### Build Fails
- Check build logs for errors
- Verify `requirements.txt` is correct
- Ensure Python version is compatible

### Database Connection Errors
- Verify PostgreSQL service is running
- Check that `DATABASE_URL` is automatically set by Railway
- If not, manually link the PostgreSQL service to your web service
- The app auto-detects `DATABASE_URL` - no manual DB config needed!

### Static Files Not Loading
- Add to start command: `python manage.py collectstatic --noinput`
- Or run manually in Railway shell

### 500 Errors
- Check logs in Railway dashboard
- Verify `DEBUG=False` and `ALLOWED_HOSTS` are set
- Check database migrations ran successfully

## Next Steps After Deployment

1. ✅ Test user registration
2. ✅ Test login/logout
3. ✅ Create a test entry
4. ✅ Test password reset
5. ✅ Test all major features
6. ✅ Set up custom domain (optional)
7. ✅ Configure backups (Railway has automatic backups)

## Railway Dashboard

Once deployed, you can:
- View logs in real-time
- Monitor usage and costs
- Scale resources
- Manage environment variables
- View metrics

## Cost Estimate

- **Free tier:** $5 credit/month (usually enough for small apps)
- **After free tier:** ~$5-10/month for small traffic
- **Database:** Included in free tier

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: Very active community
- Email support available

---

**Ready to deploy?** Follow these steps and your app will be live in 10-15 minutes!

