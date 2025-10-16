# Home Setup Guide - SQL Server Migration

**For use on your home machine after pulling the
 latest branch changes**

---

## Prerequisites

- SQL Server Express installed at home
- Git repository synced (branch: `feature/at-home` or your current branch)
- Python 3.13 installed
- All project files from work machine synced

---

## Step-by-Step Setup Instructions

### Step 1: Pull Latest Changes from Repository

```powershell
# Navigate to project directory
cd "path\to\derivco-stores-infrastructure-admin"

# Pull latest changes
git pull origin feature/at-home

# Verify you have the backend folder
dir backend
```

**Expected:** You should see `backend/` folder with `database/` subfolder

---

### Step 2: Create Database on Home SQL Server

**Option A: Using SQL Server Management Studio
 (SSMS)**

1. Open SSMS
2. Connect to: `localhost\SQLEXPRESS` (Windows Authentication)
3. Open file: `CREATE_DATABASE.sql`
4. Press **F5** to execute
5. Verify success messages appear

Option B: Using Command Line

```powershell
# Run from project directory
sqlcmd -S localhost\SQLEXPRESS -E -i "CREATE_DATABASE.sql"
```

**Expected Output:**

```bash
Database created successfully: DerivcoDurbanFacilities
Login created: facilities_admin
User created: facilities_admin
User granted db_owner role
```

---

### Step 3: Configure Environment for Home Machine

**Check if .env file exists:**

```powershell
# Check if .env exists
dir .env
```

**If .env exists:**

Open `.env` and verify/update these settings:

```env
# SQL Server Configuration - Windows Authentication
SQL_SERVER_HOST=localhost\SQLEXPRESS
SQL_SERVER_DATABASE=DerivcoDurbanFacilities
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
SQL_SERVER_USE_WINDOWS_AUTH=True

# SQLAlchemy Configuration
SQL_ECHO=False
```

**If .env does NOT exist:**

```powershell
# Copy template
copy .env.example .env

# Edit the file
notepad .env
```

Update with home SQL Server settings:

```env
SQL_SERVER_HOST=localhost\SQLEXPRESS
SQL_SERVER_DATABASE=DerivcoDurbanFacilities
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
SQL_SERVER_USE_WINDOWS_AUTH=True
SQL_ECHO=False

FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=derivco-facilities-dev-secret-key-change-in-production

JWT_SECRET_KEY=derivco-jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600

LOG_LEVEL=INFO
MIGRATION_MODE=parallel
```

---

### Step 4: Install Python Dependencies

```powershell
# Upgrade SQLAlchemy first (for Python 3.13 compatibility)
pip install --upgrade SQLAlchemy

# Install all dependencies
pip install -r requirements.txt
```

**If pyodbc fails to install:**

```powershell
# Install pre-built wheel
pip install --only-binary :all: pyodbc

# Then retry
pip install -r requirements.txt
```

---

### Step 5: Initialize Database Tables

```powershell
# Create all tables, indexes, and seed initial data
python backend/database/init_db.py --seed --verify
```

**Expected Output:**

```bash
================================================================================
DATABASE INITIALIZATION - Derivco Facilities Management
================================================================================

[1/4] Initializing database connection...
✓ Successfully connected to SQL Server: DerivcoDurbanFacilities

[2/4] Creating database tables...
[3/4] Verifying tables...
   Created 15 tables:
   ✓ AuditLog
   ✓ Categories
   ✓ Equipment
   ... (and more)

[4/4] Creating additional indexes...
   ✓ Created index: IX_Items_CategoryStore
   ... (and more)

DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!
```

---

### Step 6: Migrate Data from Excel to SQL Server

**Validate migration first (dry run):**

```powershell
python backend/database/migrate_data.py --validate
```

**Expected Output:**

```bash
✓ Inventory file found: STORES_INFRASTRUCTURE_ADMINISTRATION_enhanced.xlsx
✓ Sign-Out file found: signout_data_improved.xlsx
✓ Medical file found: medication_data_enhanced.xlsx
```

**Execute migration:**

```powershell
python backend/database/migrate_data.py --execute
```

**Expected Output:**

```bash
✓ Migrated Electric: 10 items
✓ Migrated Plumbing: 8 items
... (all categories)
✓ Total inventory items migrated: 45

MIGRATION COMPLETED SUCCESSFULLY!
```

---

### Step 7: Test Application

```powershell
# Start Flask application
python app.py
```

**Expected Output:**

```bash
Successfully loaded data from 13 sheets
 * Running on http://127.0.0.1:5001
```

**Open browser:** `http://127.0.0.1:5001`

---

## Troubleshooting

### Issue 1: "Cannot connect to SQL Server"

**Check SQL Server is running:**

```powershell
# Check service status
Get-Service MSSQL*

# Start if stopped
Start-Service MSSQL$SQLEXPRESS
```

**Verify instance name:**

```powershell
sqlcmd -L
```

Should show: `localhost\SQLEXPRESS`

---

### Issue 2: "Database does not exist"

**Solution:** Re-run database creation:

```powershell
sqlcmd -S localhost\SQLEXPRESS -E -i "CREATE_DATABASE.sql"
```

---

### Issue 3: "Module not found: pyodbc"

**Solution:**

```powershell
pip install --upgrade SQLAlchemy
pip install --only-binary :all: pyodbc
```

---

### Issue 4: "ODBC Driver not found"

**Download and install:**

- ODBC Driver 17 for SQL Server: <https://aka.ms/downloadmsodbcsql>

**Verify installation:**

```powershell
odbcad32
```

Check "ODBC Driver 17 for SQL Server" appears in the list.

---

### Issue 5: SQLAlchemy compatibility error with Python 3.13

**Solution:**

```powershell
pip install --upgrade SQLAlchemy
```

Should install SQLAlchemy 2.0.36+ which has Python 3.13 fixes.

---

### Issue 6: "TemplateNotFound" or old Excel data showing

**This is expected!** The SQL Server backend is separate from the Flask app's Excel data loading.

**To integrate SQL Server with Flask app:**

1. The current `app.py` still loads Excel files
2. Backend SQL Server is ready but not yet integrated into routes
3. For now, both systems run in parallel (set `MIGRATION_MODE=parallel`)

---

## Quick Reference Commands

```powershell
# 1. Pull latest code
git pull origin feature/at-home

# 2. Create database
sqlcmd -S localhost\SQLEXPRESS -E -i "CREATE_DATABASE.sql"

# 3. Install dependencies
pip install --upgrade SQLAlchemy
pip install -r requirements.txt

# 4. Initialize database
python backend/database/init_db.py --seed --verify

# 5. Migrate data
python backend/database/migrate_data.py --execute

# 6. Run application
python app.py
```

---

## Files You Need

These files should be in your repository:

```bash
✓ CREATE_DATABASE.sql              # Database creation script
✓ .env.example                     # Environment template
✓ requirements.txt                 # Python dependencies
✓ backend/database/connection.py   # Database connection manager
✓ backend/database/models.py       # ORM models
✓ backend/database/init_db.py      # Table initialization
✓ backend/database/migrate_data.py # Data migration script
✓ HOME_SETUP_GUIDE.md              # This file
```

---

## Environment Differences: Work vs Home

| Setting | Work Machine | Home Machine |
|---------|-------------|--------------|
| SQL Server | `localhost\SQLEXPRESS` | `localhost\SQLEXPRESS` |
| Authentication | Windows Auth | Windows Auth |
| Database | `DerivcoDurbanFacilities` | `DerivcoDurbanFacilities` |
| Branch | `feature/at-home` | `feature/at-home` |
| Data | Already migrated | Need to migrate |

---

## Verification Checklist

Before running the app, verify:

- [ ] Git repository synced with latest changes
- [ ] SQL Server Express running (`Get-Service MSSQL*`)
- [ ] Database created (`DerivcoDurbanFacilities` exists)
- [ ] `.env` file configured with home SQL Server settings
- [ ] Python dependencies installed (`pip list | Select-String "SQLAlchemy"`)
- [ ] Database tables initialized (15 tables created)
- [ ] Data migrated (45+ inventory items)
- [ ] Application starts without errors (`python app.py`)

---

## Expected Timeline

- **Step 1-2 (Git & Database):** 5 minutes
- **Step 3 (Environment):** 2 minutes
- **Step 4 (Dependencies):** 5 minutes
- **Step 5 (Initialize):** 2 minutes
- **Step 6 (Migrate):** 3 minutes
- **Step 7 (Test):** 1 minute

**Total:** ~20 minutes to fully operational

---

## Important Notes

1. **Database is local to each machine** - Work and home have separate databases
2. **Excel files are source of truth** during parallel mode - Both systems sync from Excel
3. **Windows Authentication** - No username/password needed on either machine
4. **.env file is NOT in Git** - Create it fresh on home machine (for security)
5. **Both machines use same branch** - Code is identical, only database connection differs

---

## Next Steps After Home Setup

Once everything works on home machine:

1. **Test all inventory operations** - Verify data loads correctly
2. **Compare work vs home** - Should have identical data (45 items)
3. **Continue development** - Both machines ready for SQL Server integration
4. **Switch to sql_only mode** - When ready: Set `MIGRATION_MODE=sql_only` in `.env`

---

## Getting Help

If you encounter issues:

1. **Check SQL Server status:** `Get-Service MSSQL*`
2. **Test database connection:**

   ```powershell
   sqlcmd -S localhost\SQLEXPRESS -E -Q "SELECT @@VERSION"
   ```

3. **Verify `.env` settings:** Check `SQL_SERVER_HOST=localhost\SQLEXPRESS`
4. **Review error messages** in PowerShell output
5. **Check logs:** Look for `app.log` in project directory

---

**Prepared by:** Sifiso Cyprian Shezi
**Date:** January 2025
**Purpose:** Home machine SQL Server setup for continued development
**Status:** Ready for deployment
