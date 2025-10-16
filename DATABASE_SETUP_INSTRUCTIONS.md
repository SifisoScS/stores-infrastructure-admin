# Database Setup Instructions

## Executing CREATE_DATABASE.sql Script

### Method 1: SQL Server Management Studio (SSMS) ⭐ Recommended

1. **Open SQL Server Management Studio (SSMS)**
   - Launch SSMS from Start Menu

2. **Connect to Your SQL Server Instance**
   - Server name: `localhost` or `.\SQLEXPRESS` (for SQL Server Express)
   - Authentication:
     - Windows Authentication (recommended for local dev)
     - OR SQL Server Authentication (username: `sa`, password: your SA password)
   - Click **Connect**

3. **Open the SQL Script**
   - Menu: **File** → **Open** → **File...**
   - Navigate to: `C:\users\sifisos\onedrive - derivco (pty) limited\desktop\sifiso_shezi\derivco-stores-infrastructure-admin\`
   - Select: `CREATE_DATABASE.sql`
   - Click **Open**

4. **Review the Script** (Optional but Recommended)
   - Check the file paths match your SQL Server installation
   - Default path: `C:\Program Files\Microsoft SQL Server\MSSQL15.SQLEXPRESS\MSSQL\DATA\`
   - Modify if your SQL Server uses different paths

5. **Execute the Script**
   - Click **Execute** button (or press `F5`)
   - Watch the **Messages** pane for success confirmations

6. **Verify Success**
   - You should see messages like:

     ```bash
     Database created successfully: DerivcoDurbanFacilities
     Login created: facilities_admin
     User created: facilities_admin
     User granted db_owner role
     ```

7. **Verify Database in Object Explorer**
   - Expand **Databases** node in Object Explorer
   - You should see **DerivcoDurbanFacilities** database
   - Expand it to verify it's accessible

---

### Method 2: Command Line with sqlcmd

1. **Open Command Prompt or PowerShell as Administrator**

2. **Navigate to Project Directory**

   ```powershell
   cd "C:\users\sifisos\onedrive - derivco (pty) limited\desktop\sifiso_shezi\derivco-stores-infrastructure-admin"
   ```

3. **Execute Script with sqlcmd**

   **For Windows Authentication:**

   ```powershell
   sqlcmd -S localhost -E -i CREATE_DATABASE.sql
   ```

   **For SQL Server Authentication:**

   ```powershell
   sqlcmd -S localhost -U sa -P YourSAPassword -i CREATE_DATABASE.sql
   ```

   Replace `YourSAPassword` with your actual SA password

4. **Verify Success**
   - Check for success messages in the output
   - No error messages should appear

---

### Method 3: Azure Data Studio

1. **Open Azure Data Studio**

2. **Connect to SQL Server**
   - Click **New Connection**
   - Server: `localhost` or `.\SQLEXPRESS`
   - Authentication type: Windows Authentication or SQL Login
   - Click **Connect**

3. **Open SQL File**
   - Menu: **File** → **Open File**
   - Select `CREATE_DATABASE.sql`

4. **Run Script**
   - Click **Run** button (or press `Ctrl+Shift+E`)
   - Check **Messages** pane for success confirmations

---

## Troubleshooting

### Issue: "CREATE DATABASE permission denied"

**Solution:**

- Ensure you're logged in with administrator privileges
- For Windows Auth: Run SSMS as Administrator
- For SQL Auth: Use `sa` account or account with `sysadmin` role

### Issue: "Database already exists"

**Solution:**

- Uncomment lines 14-18 in CREATE_DATABASE.sql to drop existing database
- **CAUTION:** This will delete all existing data!

### Issue: "Cannot open file" or "Access denied" for .mdf/.ldf files

**Solution:**

- Verify file paths in the script match your SQL Server installation
- Check SQL Server service account has write permissions to the DATA folder
- Try different path: `C:\SQLData\` (create folder first, grant permissions)

### Issue: "Operating system error 5 (Access denied)"

**Solution:**

- Grant SQL Server service account full control to DATA folder
- Right-click DATA folder → Properties → Security → Edit
- Add SQL Server service account (usually `NT Service\MSSQLSERVER`)
- Grant Full Control

---

## Verification Steps

After successful database creation, verify with these queries:

### Check Database Exists

```sql
USE master;
SELECT name, database_id, create_date
FROM sys.databases
WHERE name = 'DerivcoDurbanFacilities';
```

### Check Database Size

```sql
USE DerivcoDurbanFacilities;
EXEC sp_spaceused;
```

### Check Login and User

```sql
-- Check login exists
SELECT name, type_desc, create_date
FROM sys.server_principals
WHERE name = 'facilities_admin';

-- Check user exists and role membership
USE DerivcoDurbanFacilities;
SELECT dp.name AS user_name, dp.type_desc,
       STRING_AGG(drm.role_principal_id, ', ') AS roles
FROM sys.database_principals dp
LEFT JOIN sys.database_role_members drm ON dp.principal_id = drm.member_principal_id
WHERE dp.name = 'facilities_admin'
GROUP BY dp.name, dp.type_desc;
```

---

## Next Steps After Database Creation

Once database is created successfully, proceed with these steps:

### 1. Configure Environment Variables (5 minutes)

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file with your credentials
notepad .env
```

Update these values in `.env`:

```env
SQL_SERVER_HOST=localhost
SQL_SERVER_DATABASE=DerivcoDurbanFacilities
SQL_SERVER_USERNAME=facilities_admin
SQL_SERVER_PASSWORD=FacilitiesPass123!
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server
```

### 2. Install Python Dependencies (5 minutes)

```powershell
pip install -r requirements.txt
```

### 3. Initialize Database Tables (2 minutes)

```powershell
python backend/database/init_db.py --seed --verify
```

This will create all 15 tables, indexes, and seed initial data.

### 4. Migrate Data from Excel (10 minutes)

```powershell
# Validate migration first (dry run)
python backend/database/migrate_data.py --validate

# Execute actual migration
python backend/database/migrate_data.py --execute
```

### 5. Test Application (5 minutes)

```powershell
python app.py
```

Open browser: `http://127.0.0.1:5000`

---

## Success Checklist

- [ ] CREATE_DATABASE.sql executed without errors
- [ ] Database `DerivcoDurbanFacilities` visible in SSMS Object Explorer
- [ ] Login `facilities_admin` created
- [ ] User `facilities_admin` has db_owner permissions
- [ ] `.env` file configured with correct credentials
- [ ] Python dependencies installed
- [ ] Database tables initialized (15 tables created)
- [ ] Data migrated from Excel to SQL Server
- [ ] Flask application connects to SQL Server successfully

---

## Additional Notes

### Default Password

The script creates user `facilities_admin` with password: `FacilitiesPass123!`

**IMPORTANT:** Change this password in production:

```sql
ALTER LOGIN facilities_admin WITH PASSWORD = 'YourSecurePassword!';
```

### Database File Locations

Default locations (SQL Server 2019 Express):

- Data file: `C:\Program Files\Microsoft SQL Server\MSSQL15.SQLEXPRESS\MSSQL\DATA\DerivcoDurbanFacilities.mdf`
- Log file: `C:\Program Files\Microsoft SQL Server\MSSQL15.SQLEXPRESS\MSSQL\DATA\DerivcoDurbanFacilities_log.ldf`

If you have a different SQL Server version, update paths in CREATE_DATABASE.sql:

- SQL Server 2017: `MSSQL14.SQLEXPRESS`
- SQL Server 2016: `MSSQL13.SQLEXPRESS`
- SQL Server 2022: `MSSQL16.SQLEXPRESS`

### Backup Recommendation

After successful setup and data migration, create immediate backup:

```sql
BACKUP DATABASE DerivcoDurbanFacilities
TO DISK = 'C:\Backup\DerivcoDurbanFacilities_Initial.bak'
WITH FORMAT, INIT, NAME = 'Initial Backup after Migration';
```

---

**Prepared by:** Sifiso Cyprian Shezi
**Facilities Assistant Level 1 — Derivco Durban**
**Date:** September 30, 2025
**Status:** Ready for Database Creation
