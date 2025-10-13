# PostgreSQL Migration Guide

This guide will help you complete the migration from SQLite to PostgreSQL (Supabase).

## What Has Been Done

✅ Updated `requirements.txt` with PostgreSQL dependencies:
   - `psycopg2-binary==2.9.11` (PostgreSQL adapter)
   - `dj-database-url==3.0.1` (Database URL parser)

✅ Installed the PostgreSQL dependencies

✅ Updated `config/settings.py` to support PostgreSQL via `DATABASE_URL`

✅ Exported all data from SQLite to `data_backup.json`

✅ Updated `.env` file with PostgreSQL connection string

## What You Need To Do

### Step 1: Add Your Supabase Password

Open the `.env` file in the backend directory and replace `[YOUR-PASSWORD]` with your actual Supabase database password:

```env
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@db.eajeqvtnldkhjqbjhzfe.supabase.co:5432/postgres
```

**IMPORTANT**: Never commit your actual password to version control!

### Step 2: Run Migrations on PostgreSQL

Once you've added your password, run the migrations to create all tables in PostgreSQL:

```powershell
cd C:\Users\aptod\OneDrive\Desktop\real-Estate\real-estate-backend
python manage.py migrate
```

This will create all the necessary tables in your Supabase PostgreSQL database.

### Step 3: Import Your Data

After migrations complete successfully, import your existing data:

```powershell
python import_data.py
```

Or alternatively:

```powershell
python manage.py loaddata data_backup.json
```

### Step 4: Verify the Migration

1. Start your Django development server:
   ```powershell
   python manage.py runserver
   ```

2. Check that your application works correctly with the new database

3. Verify that all your data is present

## Connection String Details

Your PostgreSQL connection uses:
- **Host**: `db.eajeqvtnldkhjqbjhzfe.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres`
- **Password**: [Your password here]

## Troubleshooting

### Connection Issues

If you get connection errors:
1. Verify your password is correct in the `.env` file
2. Check that your IP is allowed in Supabase firewall settings
3. Ensure your internet connection is working

### Migration Errors

If migrations fail:
1. Check the error message carefully
2. Ensure the database is accessible
3. Verify all dependencies are installed: `pip install -r requirements.txt`

### Data Import Errors

If data import fails:
1. Ensure migrations completed successfully first
2. Check that `data_backup.json` exists
3. Review any error messages for specific issues

## Reverting to SQLite (If Needed)

If you need to temporarily revert to SQLite:

1. Comment out the `DATABASE_URL` in `.env`:
   ```env
   # DATABASE_URL=postgresql://...
   DATABASE_ENGINE=django.db.backends.sqlite3
   DATABASE_NAME=db.sqlite3
   ```

2. Restart your Django server

## Files Modified/Created

- ✅ `requirements.txt` - Added PostgreSQL dependencies
- ✅ `config/settings.py` - Added PostgreSQL support
- ✅ `.env` - Added DATABASE_URL
- ✅ `data_backup.json` - Exported data from SQLite
- ✅ `export_data.py` - Script to export data
- ✅ `import_data.py` - Script to import data
- ✅ `POSTGRESQL_MIGRATION_GUIDE.md` - This guide

## Next Steps After Migration

1. ✅ Update `.gitignore` to ensure `.env` is not committed
2. Consider backing up your PostgreSQL database regularly
3. Monitor database performance and connection pool settings
4. Update your deployment configuration if applicable

## Support

If you encounter issues:
- Check Django logs for detailed error messages
- Review Supabase dashboard for connection logs
- Ensure all environment variables are set correctly
