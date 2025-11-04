# Railway Quick Start - Deploy in 10 Minutes! 🚀

## Prerequisites
- ✅ Your code is already on GitHub
- ✅ Email address
- ✅ 10 minutes

## Step-by-Step (With Screenshots Guidance)

### Step 1: Sign Up (2 minutes)
1. Go to **https://railway.app**
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (easiest way)
4. Authorize Railway to access your repos

### Step 2: Create Project (1 minute)
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and click: **`Kiriagoray/Trading-Journal`**
4. Railway will detect it's Django and start configuring

### Step 3: Add Database (1 minute)
1. In project dashboard, click **"+ New"**
2. Click **"Database"**
3. Select **"Add PostgreSQL"**
4. Wait for it to create (30 seconds)

**✅ Database is ready! Railway automatically links it.**

### Step 4: Set Environment Variables (3 minutes)

1. Click on your **Web Service** (the Django service)
2. Click **"Variables"** tab
3. Railway should already have `DATABASE_URL` ✅

4. Click **"+ New Variable"** and add these one by one:

```
SECRET_KEY
```
**Generate it:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output and paste as the value.

```
DEBUG
Value: False
```

```
ALLOWED_HOSTS
Value: *.railway.app
```

```
EMAIL_BACKEND
Value: django.core.mail.backends.smtp.EmailBackend
```

```
EMAIL_HOST
Value: smtp.gmail.com
```

```
EMAIL_PORT
Value: 587
```

```
EMAIL_USE_TLS
Value: True
```

```
EMAIL_HOST_USER
Value: teamjournalx@gmail.com
```

```
EMAIL_HOST_PASSWORD
Value: bvbkonsxbzzcvcwf
```

```
DEFAULT_FROM_EMAIL
Value: teamjournalx@gmail.com
```

### Step 5: Configure Start Command (1 minute)

1. Still in your Web Service, go to **"Settings"** tab
2. Find **"Start Command"**
3. Set it to:
```
python manage.py migrate && gunicorn journal_project.wsgi --bind 0.0.0.0:$PORT
```

### Step 6: Deploy! (2 minutes)

1. Railway will automatically start deploying
2. Watch the **"Deployments"** tab
3. Wait for **"Active"** status (green checkmark)
4. Click the **"Domain"** link or find URL in Settings → Domains

### Step 7: Create Admin User (2 minutes)

1. In Railway dashboard, click your Web Service
2. Click **"Deployments"** tab
3. Click the latest deployment
4. Click **"Logs"** tab
5. Or use Railway's shell (if available):
   ```bash
   railway run python manage.py createsuperuser
   ```

## ✅ You're Live!

Your app is now at: `https://your-app-name.railway.app`

## 🎉 What's Next?

1. ✅ Test registration and login
2. ✅ Create a test trade entry
3. ✅ Test all features
4. ✅ Set up custom domain (optional)

## 🆘 Troubleshooting

**Build fails?**
- Check logs in "Deployments" tab
- Verify all environment variables are set
- Make sure `SECRET_KEY` is set

**Database error?**
- Verify PostgreSQL service is running
- Check that `DATABASE_URL` exists in Variables
- Railway auto-links databases - it should work automatically

**Static files not loading?**
- This is normal - static files are collected during build
- If issues persist, check build logs

**500 errors?**
- Check logs for specific error
- Verify `DEBUG=False` and `ALLOWED_HOSTS` is set
- Ensure migrations ran successfully

## 💰 Cost

- **Free tier:** $5 credit/month (usually enough for testing)
- **After free tier:** ~$5-10/month for small traffic
- **Database:** Included in free tier

## 📞 Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: Very active community
- Check logs first - they usually show the issue

---

**That's it! Your JournalX app is live on Railway!** 🎊

