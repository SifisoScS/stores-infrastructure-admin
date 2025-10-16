-- ============================================================================
-- Derivco Facilities Management - Database Creation Script
-- ============================================================================
-- Run this script to create the database and initial setup
-- Execute in SQL Server Management Studio (SSMS) or sqlcmd
-- ============================================================================

-- Step 1: Create Database
-- ============================================================================
USE master;
GO

-- Drop database if it exists (CAUTION: Only for fresh setup)
-- IF EXISTS (SELECT name FROM sys.databases WHERE name = N'DerivcoDurbanFacilities')
-- BEGIN
--     ALTER DATABASE DerivcoDurbanFacilities SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
--     DROP DATABASE DerivcoDurbanFacilities;
-- END
-- GO

-- Create new database (using SQL Server default location)
CREATE DATABASE DerivcoDurbanFacilities;
GO

-- Set database options
ALTER DATABASE DerivcoDurbanFacilities SET RECOVERY SIMPLE;
ALTER DATABASE DerivcoDurbanFacilities SET AUTO_CLOSE OFF;
ALTER DATABASE DerivcoDurbanFacilities SET AUTO_SHRINK OFF;
GO

PRINT 'Database created successfully: DerivcoDurbanFacilities';
GO

-- Step 2: Create Database User (Optional but Recommended)
-- ============================================================================
USE DerivcoDurbanFacilities;
GO

-- Create login (if using SQL Server authentication)
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = N'facilities_admin')
BEGIN
    CREATE LOGIN facilities_admin WITH PASSWORD = N'FacilitiesPass123!';
    PRINT 'Login created: facilities_admin';
END
GO

-- Create user in database
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = N'facilities_admin')
BEGIN
    CREATE USER facilities_admin FOR LOGIN facilities_admin;
    PRINT 'User created: facilities_admin';
END
GO

-- Grant permissions
ALTER ROLE db_owner ADD MEMBER facilities_admin;
GO

PRINT 'User granted db_owner role';
GO

-- Step 3: Enable full-text search (if needed)
-- ============================================================================
-- Uncomment if you plan to use full-text search features
-- IF NOT EXISTS (SELECT * FROM sys.fulltext_catalogs WHERE name = 'FacilitiesCatalog')
-- BEGIN
--     CREATE FULLTEXT CATALOG FacilitiesCatalog AS DEFAULT;
--     PRINT 'Full-text catalog created';
-- END
-- GO

-- Step 4: Set database collation (if needed)
-- ============================================================================
-- Database uses default collation
-- To check: SELECT DATABASEPROPERTYEX('DerivcoDurbanFacilities', 'Collation')

-- Step 5: Create schemas (if needed for organization)
-- ============================================================================
-- Uncomment to create additional schemas
-- CREATE SCHEMA Inventory AUTHORIZATION dbo;
-- CREATE SCHEMA SignOut AUTHORIZATION dbo;
-- CREATE SCHEMA Medical AUTHORIZATION dbo;
-- GO

-- Step 6: Verification
-- ============================================================================
PRINT '';
PRINT '============================================================================';
PRINT 'DATABASE CREATION COMPLETE';
PRINT '============================================================================';
PRINT '';
PRINT 'Database Name: DerivcoDurbanFacilities';
PRINT 'Status: ' + CAST(DATABASEPROPERTYEX('DerivcoDurbanFacilities', 'Status') AS VARCHAR(50));
PRINT 'Recovery Model: ' + CAST(DATABASEPROPERTYEX('DerivcoDurbanFacilities', 'Recovery') AS VARCHAR(50));
PRINT '';
PRINT 'Next Steps:';
PRINT '1. Update your .env file with database credentials';
PRINT '2. Run: python backend/database/init_db.py --seed --verify';
PRINT '3. Run: python backend/database/migrate_data.py --execute';
PRINT '';
PRINT '============================================================================';
GO