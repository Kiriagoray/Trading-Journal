# Deployment Fix for 500 Errors

## Issues Found and Fixed:

1. **Duplicate template filter** - Fixed `get_item` filter in `journal_extras.py`
2. **Template syntax error** - Fixed nested dictionary access in lot size calculator template
3. **Missing migrations** - Ensure migrations are run on Render

## Steps to Fix on Render:

1. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

2. **Collect Static Files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Check Render Logs:**
   - Go to your Render dashboard
   - Check the logs for specific error messages
   - Common issues:
     - Missing database migrations
     - Missing static files
     - Import errors
     - Template syntax errors

## Quick Fix Commands for Render:

Add these to your Render build command or run manually:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

## Common 500 Error Causes:

1. **Database Schema Mismatch** - Run migrations
2. **Missing Static Files** - Run collectstatic
3. **Import Errors** - Check Python path and imports
4. **Template Errors** - Check template syntax
5. **Missing Environment Variables** - Check Render environment settings

