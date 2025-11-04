# Deployment Guide for JournalX

This guide will help you deploy JournalX to production.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL (recommended for production) or SQLite (for small deployments)
- Web server (Nginx, Apache, or cloud platform)
- Domain name (optional but recommended)

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Security
SECRET_KEY=your-secret-key-here-generate-a-strong-one
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost

# Database (for PostgreSQL)
USE_POSTGRESQL=True
DB_NAME=trading_journal
DB_USER=postgres_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## Installation Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd journal_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # If you have an example file
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Set up media directory**
   ```bash
   mkdir -p media/journal/after_trade
   mkdir -p media/journal/pre_trade
   mkdir -p media/journal/backtesting
   mkdir -p media/journal/pre_trade_outcomes
   ```

## Production Deployment Options

### Option 1: Deploy to Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: gunicorn journal_project.wsgi --log-file -
   ```
3. Add `gunicorn` to requirements.txt
4. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com
   git push heroku main
   ```

### Option 2: Deploy with Nginx + Gunicorn

1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```

2. Create systemd service file `/etc/systemd/system/journalx.service`:
   ```ini
   [Unit]
   Description=JournalX Gunicorn daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/journal_project
   ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind unix:/path/to/journal_project/journalx.sock journal_project.wsgi

   [Install]
   WantedBy=multi-user.target
   ```

3. Configure Nginx:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location /static/ {
           alias /path/to/journal_project/staticfiles/;
       }

       location /media/ {
           alias /path/to/journal_project/media/;
       }

       location / {
           proxy_pass http://unix:/path/to/journal_project/journalx.sock;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Option 3: Deploy to Cloud Platforms

- **AWS Elastic Beanstalk**: Use the provided configuration
- **DigitalOcean App Platform**: Follow their Django deployment guide
- **Railway**: Connect your GitHub repo and configure environment variables
- **Render**: Connect repo and set environment variables

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use a strong, unique `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain(s)
- [ ] Enable HTTPS/SSL
- [ ] Use PostgreSQL in production (not SQLite)
- [ ] Set up proper file permissions
- [ ] Configure CORS if needed
- [ ] Set up regular database backups
- [ ] Use environment variables for sensitive data
- [ ] Enable Django's security middleware
- [ ] Set `SECURE_SSL_REDIRECT=True` if using HTTPS
- [ ] Set `SESSION_COOKIE_SECURE=True` for HTTPS
- [ ] Set `CSRF_COOKIE_SECURE=True` for HTTPS

## Post-Deployment

1. **Test the application**
   - Create a test user
   - Test all features
   - Verify email sending works
   - Check static files are served correctly

2. **Set up monitoring**
   - Configure error logging
   - Set up uptime monitoring
   - Monitor database performance

3. **Backup strategy**
   - Set up automated database backups
   - Backup media files regularly

## Troubleshooting

- **Static files not loading**: Run `collectstatic` and check STATIC_ROOT
- **Media files not loading**: Check MEDIA_ROOT and file permissions
- **Database errors**: Verify database connection and run migrations
- **Email not sending**: Check EMAIL_* environment variables
- **500 errors**: Check DEBUG=False and review error logs

## Support

For issues or questions, check the project README or create an issue in the repository.
