# Email Setup Guide for Password Reset

## Problem
Currently, password reset emails are being printed to the console instead of being sent to your Gmail inbox.

## Solution: Configure Gmail SMTP

### Step 1: Enable 2-Step Verification on Gmail
1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** on the left sidebar
3. Under **Signing in to Google**, enable **2-Step Verification** (if not already enabled)
4. Follow the prompts to complete the setup

### Step 2: Generate Gmail App Password
1. While still in Security settings, find **2-Step Verification**
2. Scroll down and click **App passwords** (you may need to sign in again)
3. Select **Mail** as the app and **Other (Custom name)** as the device
4. Enter a name like "Trading Journal Django"
5. Click **Generate**
6. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)

### Step 3: Set Environment Variables

You have two options:

#### Option A: Set Environment Variables in Command Prompt (Windows)
Before running the server, open Command Prompt and run:

```cmd
set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
set EMAIL_HOST_USER=your-email@gmail.com
set EMAIL_HOST_PASSWORD=your-16-character-app-password
set DEFAULT_FROM_EMAIL=your-email@gmail.com
```

Then run your server:
```cmd
python manage.py runserver
```

#### Option B: Create a `.env` File (Recommended)
1. Create a file named `.env` in the `journal_project` folder (same level as `manage.py`)
2. Add the following content:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

3. Replace `your-email@gmail.com` with your actual Gmail address
4. Replace `your-16-character-app-password` with the app password you generated (remove spaces: `abcdefghijklmnop`)

### Step 4: Install python-dotenv (if using .env file)
If you're using Option B, install python-dotenv:

```cmd
pip install python-dotenv
```

### Step 5: Restart the Server
After setting the environment variables, restart your Django server:

```cmd
python manage.py runserver
```

### Step 6: Test
1. Go to the login page
2. Click "Forgot Password?"
3. Enter your email address
4. Check your Gmail inbox (and spam folder) for the reset email

## Troubleshooting

### Email still not received?
1. **Check spam folder** - Sometimes Gmail filters password reset emails
2. **Verify app password** - Make sure you copied the full 16-character password without spaces
3. **Check server logs** - Look for any error messages in the terminal where you're running the server
4. **Verify email address** - Make sure the email address exists in your Django user database

### Common Errors

**"SMTPAuthenticationError"**
- Double-check your Gmail email address and app password
- Make sure 2-Step Verification is enabled
- Ensure you're using an App Password, not your regular Gmail password

**"Connection refused"**
- Check your internet connection
- Some networks block SMTP (port 587). Try using port 465 with SSL instead

### Alternative: Use Console Backend for Testing
If you just want to test the password reset flow without sending real emails, you can keep using the console backend. The reset link will be printed in your terminal - just copy and paste it into your browser.

## Security Note
- Never commit your `.env` file to Git (it should already be in `.gitignore`)
- Never share your Gmail App Password
- Each app should have its own App Password

