# Deployment Guide - Ray's Trading Journal

## PostgreSQL Configuration

The app is configured to easily switch between SQLite (development) and PostgreSQL (production).

### Environment Variables

Set the following environment variables to use PostgreSQL:

```bash
export USE_POSTGRESQL=true
export DB_NAME=trading_journal
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
```

Or for Windows:
```cmd
set USE_POSTGRESQL=true
set DB_NAME=trading_journal
set DB_USER=postgres
set DB_PASSWORD=your_password
set DB_HOST=localhost
set DB_PORT=5432
```

### Install PostgreSQL Driver

```bash
pip install psycopg2-binary
```

### Migrate Database

After setting up PostgreSQL, run:

```bash
python manage.py migrate
python manage.py setup_choice_categories
```

## Production Settings Checklist

Before deploying to production:

1. **Security Settings:**
   - Set `DEBUG = False` (via `DEBUG=false` environment variable)
   - Set a strong `SECRET_KEY` (via `SECRET_KEY` environment variable)
   - Configure `ALLOWED_HOSTS` (via `ALLOWED_HOSTS=yourdomain.com`)

2. **Static Files:**
   ```bash
   python manage.py collectstatic
   ```

3. **Media Files:**
   - Ensure `MEDIA_ROOT` is writable
   - Configure your web server to serve media files (or use cloud storage)

4. **Database:**
   - Use PostgreSQL for production
   - Backup regularly

5. **HTTPS:**
   - Configure SSL/TLS certificates
   - Update `CSRF_TRUSTED_ORIGINS` if needed

## Configuration System

The app includes a configuration model system for managing dropdown options.

### Initialize Choice Categories

Run this command after first migration:

```bash
python manage.py setup_choice_categories
```

This creates all choice categories and options in the database. You can then manage them through the Django admin panel.

### Managing Choices via Admin

1. Go to `/admin/`
2. Navigate to "Choice Categories" or "Choice Options"
3. Add, edit, or deactivate options
4. Changes take effect immediately (no code changes needed)

## Mobile Responsiveness

The app is fully responsive and includes:
- Collapsible sidebar on mobile
- Adaptive navigation with icon-only mode on small screens
- Touch-friendly buttons and form elements
- Optimized card layouts for mobile

## HTMX Integration

HTMX is integrated for smooth page transitions:
- Navigation links use `hx-boost` for AJAX navigation
- Page transitions are smooth with fade effects
- Mobile sidebar auto-closes after navigation

To disable HTMX for specific links, remove `hx-boost` attribute.

