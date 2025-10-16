# SQL Server Setup Guide

**Derivco Facilities Management System - Database Migration**

This guide will help you set up SQL Server and migrate from Excel-based storage to enterprise-grade SQL Server database.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [SQL Server Installation](#sql-server-installation)
3. [Database Setup](#database-setup)
4. [Environment Configuration](#environment-configuration)
5. [Dependencies Installation](#dependencies-installation)
6. [Database Initialization](#database-initialization)
7. [Data Migration](#data-migration)
8. [Testing & Verification](#testing--verification)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.8+** (already installed)
- **SQL Server 2019+** or **Azure SQL Database**
- **ODBC Driver 17 for SQL Server** (or later)
- **SQL Server Management Studio (SSMS)** (optional, for GUI management)

### System Requirements
- Windows 10/11 or Windows Server 2016+
- Minimum 4GB RAM (8GB+ recommended)
- 10GB+ free disk space for SQL Server

---

## SQL Server Installation

### Option 1: SQL Server Express (Free, Local Development)

1. **Download SQL Server Express**
   - Visit: https://www.microsoft.com/en-us/sql-server/sql-server-downloads
   - Download "SQL Server 2022 Express"
   - Choose "Custom" installation

2. **Install SQL Server Express**
   ```powershell
   # Run installer and select:
   - Installation Type: New SQL Server stand-alone installation
   - Features: Database Engine Services
   - Instance Configuration: Default instance
   - Server Configuration: Use default service accounts
   - Database Engine Configuration: Mixed Mode Authentication
   - Set SA password: YourSecurePassword123!
   - Add current user as SQL Server administrator
   ```

3. **Verify Installation**
   ```powershell
   # Open Command Prompt and run:
   sqlcmd -S localhost -U sa -P YourSecurePassword123!

   # If successful, you'll see:
   # 1>

   # Type 'exit' to quit
   ```

### Option 2: Azure SQL Database (Cloud, Production)

1. **Create Azure SQL Database**
   - Sign in to Azure Portal: https://portal.azure.com
   - Create new resource → "SQL Database"
   - Fill in details:
     - Database name: `DerivcoDurbanFacilities`
     - Server: Create new server
     - Pricing tier: Basic or Standard

2. **Configure Firewall**
   - In Azure Portal, go to SQL Server → Firewall settings
   - Add client IP address
   - Allow Azure services access

3. **Get Connection String**
   - Database → Connection strings
   - Copy ADO.NET connection string

### Option 3: Existing SQL Server

If you already have SQL Server installed, ensure:
- SQL Server Browser service is running
- TCP/IP protocol is enabled
- Mixed Mode Authentication is configured
- Firewall allows SQL Server port (default: 1433)

---

## Database Setup

### Create Database

Using **SQL Server Management Studio (SSMS)**:
```sql
-- Connect to SQL Server and run:
CREATE DATABASE DerivcoDurbanFacilities
GO

USE DerivcoDurbanFacilities
GO
```

Using **Command Line (sqlcmd)**:
```powershell
sqlcmd -S localhost -U sa -P YourSecurePassword123!
```
```sql
CREATE DATABASE DerivcoDurbanFacilities
GO
```

### Create Database User (Optional, Recommended)

```sql
USE DerivcoDurbanFacilities
GO

-- Create login
CREATE LOGIN facilities_admin WITH PASSWORD = 'FacilitiesPass123!';
GO

-- Create user
CREATE USER facilities_admin FOR LOGIN facilities_admin;
GO

-- Grant permissions
ALTER ROLE db_owner ADD MEMBER facilities_admin;
GO
```

---

## Environment Configuration

### 1. Copy Environment Template

```powershell
# In project root directory
copy .env.example .env
```

### 2. Edit .env File

Open `.env` in your text editor and configure:

#### For Local SQL Server Express:
```env
# SQL Server Configuration
SQL_SERVER_HOST=localhost
SQL_SERVER_DATABASE=DerivcoDurbanFacilities
SQL_SERVER_USERNAME=sa
SQL_SERVER_PASSWORD=YourSecurePassword123!
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
SQL_SERVER_USE_WINDOWS_AUTH=False

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=change-this-to-random-32-character-string

# JWT Configuration
JWT_SECRET_KEY=change-this-to-random-32-character-jwt-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Application Settings
SQL_ECHO=False
LOG_LEVEL=INFO
MIGRATION_MODE=parallel
```

#### For Azure SQL Database:
```env
# SQL Server Configuration
SQL_SERVER_HOST=your-server.database.windows.net
SQL_SERVER_DATABASE=DerivcoDurbanFacilities
SQL_SERVER_USERNAME=facilities_admin
SQL_SERVER_PASSWORD=YourAzurePassword123!
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
SQL_SERVER_USE_WINDOWS_AUTH=False

# Rest of configuration same as above
```

#### For Windows Authentication (Domain):
```env
SQL_SERVER_HOST=localhost
SQL_SERVER_DATABASE=DerivcoDurbanFacilities
SQL_SERVER_USE_WINDOWS_AUTH=True
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
```

### 3. Generate Secure Keys

```python
# Generate secure secret keys (run in Python)
import secrets
print("SECRET_KEY:", secrets.token_hex(32))
print("JWT_SECRET_KEY:", secrets.token_hex(32))
```

---

## Dependencies Installation

### Install ODBC Driver

#### Windows:
1. Download from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
2. Run installer: `msodbcsql.msi`
3. Follow installation wizard

Verify installation:
```powershell
# List installed ODBC drivers
odbcad32
```

### Install Python Dependencies

```powershell
# Install all required packages
pip install -r requirements.txt

# Or install SQL Server specific packages only:
pip install pyodbc SQLAlchemy alembic python-dotenv
```

---

## Database Initialization

### 1. Create Database Tables

```powershell
# Run database initialization script
python backend/database/init_db.py --seed --verify
```

This will:
- ✓ Create all 15+ database tables
- ✓ Create indexes for performance
- ✓ Seed initial categories (Electric, Plumbing, etc.)
- ✓ Create default storeroom
- ✓ Verify setup completed successfully

Expected output:
```
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
   ✓ FirstAidInventory
   ✓ InventoryItems
   ... (and more)

[4/4] Creating additional indexes...
   ✓ Created index: IX_Items_CategoryStore
   ✓ Created index: IX_SignOut_EmployeeStatus
   ... (and more)

================================================================================
DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!
================================================================================
```

### 2. Test Database Connection

```python
# Run quick test
python -c "from backend.database import init_database; db = init_database(); print('✓ Connection successful!')"
```

---

## Data Migration

### Migration Modes

The system supports three migration modes:

1. **`excel_only`** (default) - Continue using Excel files
2. **`parallel`** - Use both Excel and SQL Server (recommended during migration)
3. **`sql_only`** - Use SQL Server only (after migration complete)

Set mode in `.env`:
```env
MIGRATION_MODE=parallel
```

### Migrate Data from Excel to SQL Server

```powershell
# Run migration script (creates data migration script first)
python backend/database/migrate_data.py --validate

# If validation passes, run actual migration:
python backend/database/migrate_data.py --execute
```

**Migration includes:**
- ✓ All inventory categories and items
- ✓ Sign-out transactions
- ✓ Medical incidents and first aid inventory
- ✓ Service providers and metrics
- ✓ Maintenance logs
- ✓ Supplier information

---

## Testing & Verification

### 1. Test Database Operations

```python
# Test basic CRUD operations
python backend/tests/test_database.py
```

### 2. Verify Data Integrity

```powershell
# Compare Excel vs SQL Server data
python backend/database/verify_data.py

# Expected output:
# ✓ Categories: Excel=10, SQL=10 (Match)
# ✓ Inventory Items: Excel=245, SQL=245 (Match)
# ✓ Sign-out Transactions: Excel=89, SQL=89 (Match)
# ✓ All data migrated successfully!
```

### 3. Test Application with SQL Server

```powershell
# Start Flask application
python app.py

# Application should start with SQL Server connection
# Open browser: http://127.0.0.1:5000
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: "ODBC Driver not found"
**Error:** `Data source name not found and no default driver specified`

**Solution:**
```powershell
# Install ODBC Driver 17 for SQL Server
# Download from Microsoft: https://aka.ms/downloadmsodbcsql

# Verify installation:
odbcad32
# Look for "ODBC Driver 17 for SQL Server" in list
```

#### Issue 2: "Cannot connect to SQL Server"
**Error:** `Login failed for user 'sa'`

**Solutions:**
1. Verify SQL Server is running:
   ```powershell
   # Check SQL Server service status
   Get-Service MSSQLSERVER

   # Start if stopped:
   Start-Service MSSQLSERVER
   ```

2. Check authentication mode:
   - Open SSMS
   - Right-click server → Properties → Security
   - Ensure "SQL Server and Windows Authentication mode" is selected

3. Verify credentials in `.env` file

#### Issue 3: "Named Pipes Provider error"
**Error:** `A network-related or instance-specific error occurred`

**Solutions:**
1. Enable TCP/IP protocol:
   - Open "SQL Server Configuration Manager"
   - SQL Server Network Configuration → Protocols
   - Enable TCP/IP
   - Restart SQL Server service

2. Check SQL Server Browser service:
   ```powershell
   Start-Service SQLBrowser
   ```

#### Issue 4: "Database does not exist"
**Error:** `Cannot open database "DerivcoDurbanFacilities"`

**Solution:**
```sql
-- Connect to master database and create:
USE master
GO

CREATE DATABASE DerivcoDurbanFacilities
GO
```

#### Issue 5: "Port 1433 blocked"

**Solution:**
```powershell
# Add firewall rule for SQL Server
netsh advfirewall firewall add rule name="SQL Server" dir=in action=allow protocol=TCP localport=1433
```

#### Issue 6: "pyodbc import error"

**Solution:**
```powershell
# Reinstall pyodbc
pip uninstall pyodbc
pip install pyodbc --no-cache-dir

# If still fails, try:
pip install pyodbc==5.1.0
```

---

## Database Maintenance

### Backup Database

```sql
-- Full backup
BACKUP DATABASE DerivcoDurbanFacilities
TO DISK = 'C:\Backup\DerivcoDurbanFacilities.bak'
WITH FORMAT, MEDIANAME = 'SQLServerBackups', NAME = 'Full Backup';
GO
```

### Restore Database

```sql
-- Restore from backup
RESTORE DATABASE DerivcoDurbanFacilities
FROM DISK = 'C:\Backup\DerivcoDurbanFacilities.bak'
WITH REPLACE;
GO
```

### Monitor Performance

```sql
-- Check table sizes
SELECT
    t.NAME AS TableName,
    p.rows AS RowCounts,
    SUM(a.total_pages) * 8 / 1024 AS TotalSpaceMB
FROM sys.tables t
INNER JOIN sys.indexes i ON t.OBJECT_ID = i.object_id
INNER JOIN sys.partitions p ON i.object_id = p.OBJECT_ID AND i.index_id = p.index_id
INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
WHERE t.is_ms_shipped = 0
GROUP BY t.Name, p.Rows
ORDER BY TotalSpaceMB DESC;
GO
```

---

## Next Steps

After successful SQL Server setup:

1. ✅ **Run Data Migration**
   ```powershell
   python backend/database/migrate_data.py --execute
   ```

2. ✅ **Switch to Parallel Mode**
   ```env
   MIGRATION_MODE=parallel
   ```

3. ✅ **Test Application Thoroughly**
   - Verify all inventory operations work
   - Test sign-out register functionality
   - Check medical services features
   - Validate reporting accuracy

4. ✅ **Monitor for 1-2 Weeks**
   - Compare Excel vs SQL Server data daily
   - Address any discrepancies immediately
   - Monitor performance and errors

5. ✅ **Switch to SQL-Only Mode**
   ```env
   MIGRATION_MODE=sql_only
   ```

6. ✅ **Archive Excel Files**
   - Keep as read-only backup
   - Store in secure location
   - Document final state

---

## Support & Resources

### Documentation
- **SQL Server Migration Plan:** `SQL_SERVER_MIGRATION_PLAN.md`
- **Folder Structure:** `FOLDER_STRUCTURE.md`
- **Reorganization Summary:** `REORGANIZATION_SUMMARY.md`

### SQL Server Resources
- Microsoft SQL Server Documentation: https://docs.microsoft.com/sql/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- PyODBC Documentation: https://github.com/mkleehammer/pyodbc/wiki

### Getting Help
1. Check troubleshooting section above
2. Review SQL Server error logs
3. Test connection with `sqlcmd` or SSMS
4. Verify `.env` configuration
5. Check Python dependencies are installed

---

**Prepared by:** Sifiso Cyprian Shezi
**Facilities Assistant Level 1 — Derivco Durban**
**Date:** September 30, 2025
**Version:** 1.0