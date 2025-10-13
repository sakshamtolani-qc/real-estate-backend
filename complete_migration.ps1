# PostgreSQL Migration Script
# This script completes the migration to PostgreSQL

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Migration Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if password is set
Write-Host "Step 1: Checking .env configuration..." -ForegroundColor Yellow
$envContent = Get-Content .env -Raw
if ($envContent -match '\[YOUR-PASSWORD\]') {
    Write-Host "ERROR: Please update your .env file first!" -ForegroundColor Red
    Write-Host "Replace [YOUR-PASSWORD] with your actual Supabase password in the .env file" -ForegroundColor Red
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
Write-Host "✓ .env file configured" -ForegroundColor Green
Write-Host ""

# Run migrations
Write-Host "Step 2: Running database migrations..." -ForegroundColor Yellow
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Migration failed!" -ForegroundColor Red
    Write-Host "Please check the error message above and fix any issues." -ForegroundColor Red
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
Write-Host "✓ Migrations completed successfully" -ForegroundColor Green
Write-Host ""

# Import data
Write-Host "Step 3: Importing data from SQLite backup..." -ForegroundColor Yellow
python import_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Data import failed!" -ForegroundColor Red
    Write-Host "Please check the error message above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
Write-Host "✓ Data imported successfully" -ForegroundColor Green
Write-Host ""

# Success message
Write-Host "============================================" -ForegroundColor Green
Write-Host "Migration completed successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your Django application is now using PostgreSQL (Supabase)!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Start your server: python manage.py runserver" -ForegroundColor White
Write-Host "2. Test your application to ensure everything works" -ForegroundColor White
Write-Host "3. Backup your data regularly" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
