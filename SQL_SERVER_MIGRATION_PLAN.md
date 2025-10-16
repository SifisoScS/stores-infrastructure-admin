# SQL Server Migration & Backend/Frontend Separation Plan

## 🎯 Project Overview

**Current State:** Flask application using Excel files as data storage
**Target State:** Professional enterprise application with SQL Server database and separated backend/frontend architecture
**Timeline:** Phased migration approach for minimal disruption

---

## Phase 1: Database Design & Schema Creation

### 1.1 Database Schema Design

#### Core Tables Structure

```sql
-- ============================================================================
-- INVENTORY MANAGEMENT SCHEMA
-- ============================================================================

-- Categories Table
CREATE TABLE dbo.Categories (
    CategoryID INT PRIMARY KEY IDENTITY(1,1),
    CategoryName NVARCHAR(100) NOT NULL UNIQUE,
    Description NVARCHAR(500),
    IconName NVARCHAR(50),
    DisplayOrder INT,
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME2 DEFAULT GETDATE(),
    ModifiedDate DATETIME2 DEFAULT GETDATE()
);

-- Stores/Locations Table
CREATE TABLE dbo.Stores (
    StoreID INT PRIMARY KEY IDENTITY(1,1),
    StoreName NVARCHAR(100) NOT NULL,
    Location NVARCHAR(200),
    Floor NVARCHAR(50),
    Building NVARCHAR(100),
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME2 DEFAULT GETDATE()
);

-- Inventory Items Table
CREATE TABLE dbo.InventoryItems (
    ItemID INT PRIMARY KEY IDENTITY(1,1),
    ItemCode NVARCHAR(50) NOT NULL UNIQUE,
    ItemName NVARCHAR(200) NOT NULL,
    CategoryID INT NOT NULL,
    StoreID INT NOT NULL,
    Description NVARCHAR(1000),
    UnitOfMeasure NVARCHAR(50),
    CurrentStock INT DEFAULT 0,
    MinimumStock INT DEFAULT 0,
    MaximumStock INT,
    UnitPrice DECIMAL(10,2),
    TotalValue AS (CurrentStock * UnitPrice) PERSISTED,
    Location NVARCHAR(200),
    Supplier NVARCHAR(200),
    LastRestockDate DATE,
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME2 DEFAULT GETDATE(),
    ModifiedDate DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Items_Category FOREIGN KEY (CategoryID) REFERENCES dbo.Categories(CategoryID),
    CONSTRAINT FK_Items_Store FOREIGN KEY (StoreID) REFERENCES dbo.Stores(StoreID)
);

-- Stock Movement History
CREATE TABLE dbo.StockMovements (
    MovementID INT PRIMARY KEY IDENTITY(1,1),
    ItemID INT NOT NULL,
    MovementType NVARCHAR(50) NOT NULL, -- 'IN', 'OUT', 'ADJUSTMENT', 'TRANSFER'
    Quantity INT NOT NULL,
    PreviousStock INT,
    NewStock INT,
    Reference NVARCHAR(100), -- Work Order, REQ number, etc.
    Notes NVARCHAR(500),
    CreatedBy NVARCHAR(100),
    CreatedDate DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Movement_Item FOREIGN KEY (ItemID) REFERENCES dbo.InventoryItems(ItemID)
);

-- ============================================================================
-- SIGNOUT REGISTER SCHEMA
-- ============================================================================

-- Equipment/Tools Table
CREATE TABLE dbo.Equipment (
    EquipmentID INT PRIMARY KEY IDENTITY(1,1),
    EquipmentCode NVARCHAR(50) NOT NULL UNIQUE,
    EquipmentName NVARCHAR(200) NOT NULL,
    Category NVARCHAR(100),
    Description NVARCHAR(500),
    SerialNumber NVARCHAR(100),
    PurchaseDate DATE,
    Value DECIMAL(10,2),
    Status NVARCHAR(50) DEFAULT 'Available', -- 'Available', 'Checked Out', 'Maintenance', 'Lost'
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME2 DEFAULT GETDATE()
);

-- Sign-Out Transactions
CREATE TABLE dbo.SignOutTransactions (
    TransactionID INT PRIMARY KEY IDENTITY(1,1),
    EquipmentID INT NOT NULL,
    EmployeeNumber NVARCHAR(50) NOT NULL,
    EmployeeName NVARCHAR(200) NOT NULL,
    Department NVARCHAR(100),
    WorkOrderNumber NVARCHAR(50), -- REQ/WO Number
    TaskDescription NVARCHAR(500),
    SignOutDate DATETIME2 NOT NULL,
    ExpectedReturnDate DATE,
    SignInDate DATETIME2,
    Status NVARCHAR(50) DEFAULT 'Checked Out', -- 'Checked Out', 'Returned', 'Overdue', 'Lost'
    SignOutBy NVARCHAR(100), -- Who issued it
    SignInBy NVARCHAR(100), -- Who received it back
    Notes NVARCHAR(500),
    CreatedDate DATETIME2 DEFAULT GETDATE(),
    ModifiedDate DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_SignOut_Equipment FOREIGN KEY (EquipmentID) REFERENCES dbo.Equipment(EquipmentID)
);

-- ============================================================================
-- MEDICAL SERVICES SCHEMA
-- ============================================================================

-- First Aid Inventory
CREATE TABLE dbo.FirstAidInventory (
    ItemID INT PRIMARY KEY IDENTITY(1,1),
    ItemName NVARCHAR(200) NOT NULL,
    Category NVARCHAR(100),
    CurrentStock INT DEFAULT 0,
    MinimumStock INT DEFAULT 0,
    ExpiryDate DATE,
    Location NVARCHAR(200),
    Supplier NVARCHAR(200),
    LastRestockDate DATE,
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME2 DEFAULT GETDATE()
);

-- Medical Incidents
CREATE TABLE dbo.MedicalIncidents (
    IncidentID INT PRIMARY KEY IDENTITY(1,1),
    IncidentDate DATETIME2 NOT NULL,
    EmployeeNumber NVARCHAR(50),
    EmployeeName NVARCHAR(200),
    IncidentType NVARCHAR(100), -- 'Injury', 'Illness', 'First Aid', 'Emergency'
    Severity NVARCHAR(50), -- 'Minor', 'Moderate', 'Severe', 'Critical'
    Description NVARCHAR(1000),
    TreatmentGiven NVARCHAR(1000),
    Location NVARCHAR(200),
    WitnessName NVARCHAR(200),
    ReportedBy NVARCHAR(100),
    FollowUpRequired BIT DEFAULT 0,
    FollowUpDate DATE,
    Status NVARCHAR(50) DEFAULT 'Open', -- 'Open', 'Under Investigation', 'Closed'
    CreatedDate DATETIME2 DEFAULT GETDATE(),
    ModifiedDate DATETIME2 DEFAULT GETDATE()
);

-- ============================================================================
-- SERVICE PROVIDERS SCHEMA
-- ============================================================================

-- Service Providers
CREATE TABLE dbo.ServiceProviders (
    ProviderID INT PRIMARY KEY IDENTITY(1,1),
    ProviderCode NVARCHAR(50) NOT NULL UNIQUE,
    ProviderName NVARCHAR(200) NOT NULL,
    ServiceType NVARCHAR(100), -- 'Catering', 'Cleaning', 'Garden', 'Maintenance'
    ContactPerson NVARCHAR(200),
    Email NVARCHAR(200),
    Phone NVARCHAR(50),
    Address NVARCHAR(500),
    ContractStartDate DATE,
    ContractEndDate DATE,
    ContractValue DECIMAL(15,2),
    PerformanceRating DECIMAL(3,2), -- 1.00 to 5.00
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME2 DEFAULT GETDATE(),
    ModifiedDate DATETIME2 DEFAULT GETDATE()
);

-- Service Performance Metrics
CREATE TABLE dbo.ServiceMetrics (
    MetricID INT PRIMARY KEY IDENTITY(1,1),
    ProviderID INT NOT NULL,
    MetricDate DATE NOT NULL,
    ServiceQuality DECIMAL(3,2),
    ResponseTime INT, -- in minutes
    ComplianceScore DECIMAL(5,2),
    CustomerSatisfaction DECIMAL(3,2),
    Notes NVARCHAR(500),
    CreatedDate DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Metrics_Provider FOREIGN KEY (ProviderID) REFERENCES dbo.ServiceProviders(ProviderID)
);

-- ============================================================================
-- FACILITIES MANAGEMENT SCHEMA
-- ============================================================================

-- Maintenance Log
CREATE TABLE dbo.MaintenanceLog (
    LogID INT PRIMARY KEY IDENTITY(1,1),
    WorkOrderNumber NVARCHAR(50) NOT NULL,
    REQNumber NVARCHAR(50),
    AssetType NVARCHAR(100),
    AssetLocation NVARCHAR(200),
    IssueDescription NVARCHAR(1000),
    Priority NVARCHAR(50), -- 'Low', 'Medium', 'High', 'Critical'
    AssignedTo NVARCHAR(100),
    Status NVARCHAR(50), -- 'Pending', 'In Progress', 'Completed', 'Cancelled'
    RequestedDate DATETIME2,
    StartDate DATETIME2,
    CompletedDate DATETIME2,
    TotalCost DECIMAL(10,2),
    Notes NVARCHAR(1000),
    CreatedBy NVARCHAR(100),
    CreatedDate DATETIME2 DEFAULT GETDATE(),
    ModifiedDate DATETIME2 DEFAULT GETDATE()
);

-- Suppliers & Contractors
CREATE TABLE dbo.Suppliers (
    SupplierID INT PRIMARY KEY IDENTITY(1,1),
    SupplierName NVARCHAR(200) NOT NULL,
    SupplierType NVARCHAR(100), -- 'Supplier', 'Contractor', 'Vendor'
    Category NVARCHAR(100),
    ContactPerson NVARCHAR(200),
    Email NVARCHAR(200),
    Phone NVARCHAR(50),
    Address NVARCHAR(500),
    TaxNumber NVARCHAR(50),
    BankDetails NVARCHAR(500),
    Rating DECIMAL(3,2),
    IsActive BIT DEFAULT 1,
    CreatedDate DATETIME2 DEFAULT GETDATE()
);

-- ============================================================================
-- USER MANAGEMENT & SECURITY SCHEMA
-- ============================================================================

-- Users Table
CREATE TABLE dbo.Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    EmployeeNumber NVARCHAR(50) NOT NULL UNIQUE,
    Username NVARCHAR(100) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(500) NOT NULL,
    FirstName NVARCHAR(100),
    LastName NVARCHAR(100),
    Email NVARCHAR(200),
    Phone NVARCHAR(50),
    Department NVARCHAR(100),
    JobTitle NVARCHAR(100),
    Role NVARCHAR(50), -- 'Admin', 'Manager', 'Assistant', 'User'
    IsActive BIT DEFAULT 1,
    LastLogin DATETIME2,
    CreatedDate DATETIME2 DEFAULT GETDATE(),
    ModifiedDate DATETIME2 DEFAULT GETDATE()
);

-- Audit Trail
CREATE TABLE dbo.AuditLog (
    AuditID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    ActionType NVARCHAR(100), -- 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'EXPORT'
    TableName NVARCHAR(100),
    RecordID INT,
    OldValue NVARCHAR(MAX),
    NewValue NVARCHAR(MAX),
    IPAddress NVARCHAR(50),
    Timestamp DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_Audit_User FOREIGN KEY (UserID) REFERENCES dbo.Users(UserID)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Inventory Items Indexes
CREATE INDEX IX_Items_Category ON dbo.InventoryItems(CategoryID);
CREATE INDEX IX_Items_Store ON dbo.InventoryItems(StoreID);
CREATE INDEX IX_Items_LowStock ON dbo.InventoryItems(CurrentStock, MinimumStock) WHERE IsActive = 1;

-- SignOut Transactions Indexes
CREATE INDEX IX_SignOut_Equipment ON dbo.SignOutTransactions(EquipmentID);
CREATE INDEX IX_SignOut_Employee ON dbo.SignOutTransactions(EmployeeNumber);
CREATE INDEX IX_SignOut_Status ON dbo.SignOutTransactions(Status) WHERE Status = 'Checked Out';
CREATE INDEX IX_SignOut_Overdue ON dbo.SignOutTransactions(ExpectedReturnDate, Status) WHERE Status = 'Checked Out';

-- Stock Movements Indexes
CREATE INDEX IX_Movement_Item ON dbo.StockMovements(ItemID);
CREATE INDEX IX_Movement_Date ON dbo.StockMovements(CreatedDate DESC);

-- Medical Incidents Indexes
CREATE INDEX IX_Incidents_Date ON dbo.MedicalIncidents(IncidentDate DESC);
CREATE INDEX IX_Incidents_Status ON dbo.MedicalIncidents(Status);

-- Maintenance Log Indexes
CREATE INDEX IX_Maintenance_Status ON dbo.MaintenanceLog(Status);
CREATE INDEX IX_Maintenance_Priority ON dbo.MaintenanceLog(Priority);
CREATE INDEX IX_Maintenance_WO ON dbo.MaintenanceLog(WorkOrderNumber);
```

---

## Phase 2: Backend Architecture

### 2.1 Folder Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── auth.py                      # Authentication endpoints
│   ├── inventory.py                 # Inventory CRUD operations
│   ├── signout.py                   # Sign-out register operations
│   ├── medical.py                   # Medical services operations
│   ├── providers.py                 # Service providers operations
│   ├── administration.py            # Admin portal operations
│   ├── analytics.py                 # Analytics & reporting
│   └── compliance.py                # Compliance monitoring
│
├── database/
│   ├── __init__.py
│   ├── connection.py                # SQL Server connection manager
│   ├── models.py                    # SQLAlchemy ORM models
│   ├── repositories/                # Data access layer
│   │   ├── inventory_repository.py
│   │   ├── signout_repository.py
│   │   └── ...
│   └── migrations/                  # Alembic migrations
│       ├── versions/
│       └── alembic.ini
│
├── services/                        # EXISTING - Keep and enhance
│   ├── inventory_service.py         # Enhanced with SQL queries
│   ├── analytics_engine.py
│   ├── report_generator.py
│   └── notification_system.py
│
├── core/                            # EXISTING - Keep and enhance
│   ├── excel_processor.py           # Temporary during migration
│   └── ...
│
├── utils/                           # EXISTING - Keep and enhance
│   ├── data_automation.py
│   ├── validators.py                # NEW - Input validation
│   └── formatters.py                # NEW - Data formatting
│
├── middleware/
│   ├── auth_middleware.py           # JWT authentication
│   ├── logging_middleware.py        # Request/response logging
│   └── error_handler.py             # Global error handling
│
├── config/
│   ├── __init__.py
│   ├── development.py               # Dev configuration
│   ├── production.py                # Prod configuration
│   └── testing.py                   # Test configuration
│
├── tests/
│   ├── test_api.py
│   ├── test_services.py
│   └── test_database.py
│
├── app.py                           # Flask application entry
├── requirements.txt
└── .env                             # Environment variables
```

### 2.2 Key Dependencies (requirements.txt)

```txt
# Flask Core
Flask==3.0.3
Flask-CORS==4.0.0
Flask-JWT-Extended==4.6.0

# Database
pyodbc==5.1.0                       # SQL Server driver
SQLAlchemy==2.0.27                  # ORM
alembic==1.13.1                     # Migrations
pymssql==2.2.11                     # Alternative SQL Server driver

# Data Processing
pandas==2.2.3
numpy==2.1.3

# API & Security
marshmallow==3.20.2                 # Serialization
bcrypt==4.1.2                       # Password hashing
python-dotenv==1.0.1                # Environment variables

# Monitoring & Logging
python-json-logger==2.0.7
sentry-sdk==1.40.0                  # Error tracking

# Testing
pytest==8.0.0
pytest-flask==1.3.0
```

### 2.3 SQL Server Connection (database/connection.py)

```python
import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """SQL Server database connection manager"""

    def __init__(self):
        self.server = os.getenv('SQL_SERVER_HOST')
        self.database = os.getenv('SQL_SERVER_DATABASE')
        self.username = os.getenv('SQL_SERVER_USERNAME')
        self.password = os.getenv('SQL_SERVER_PASSWORD')
        self.driver = os.getenv('SQL_SERVER_DRIVER', 'ODBC Driver 17 for SQL Server')

        # SQLAlchemy connection string
        self.connection_string = (
            f"mssql+pyodbc://{self.username}:{self.password}@{self.server}/"
            f"{self.database}?driver={self.driver}"
        )

        self.engine = None
        self.session_factory = None

    def initialize(self):
        """Initialize database connection and session factory"""
        self.engine = create_engine(
            self.connection_string,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=os.getenv('SQL_ECHO', 'False').lower() == 'true'
        )

        self.session_factory = scoped_session(
            sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        )

    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_raw_connection(self):
        """Get raw pyodbc connection for direct SQL queries"""
        conn_str = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password}"
        )
        return pyodbc.connect(conn_str)

# Global database manager instance
db_manager = DatabaseManager()

def init_database():
    """Initialize database connection"""
    db_manager.initialize()
    return db_manager
```

### 2.4 Environment Variables (.env)

```env
# SQL Server Configuration
SQL_SERVER_HOST=your-server.database.windows.net
SQL_SERVER_DATABASE=DerivcoDurbannFacilities
SQL_SERVER_USERNAME=facilities_admin
SQL_SERVER_PASSWORD=YourSecurePassword123!
SQL_SERVER_DRIVER=ODBC Driver 17 for SQL Server

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Application Settings
SQL_ECHO=False
LOG_LEVEL=INFO
```

---

## Phase 3: Frontend Architecture

```
frontend/
├── templates/                       # YOUR EXISTING organized structure
│   ├── base.html
│   ├── landing_home.html
│   ├── home_enhanced.html
│   ├── index.html
│   ├── administration/
│   ├── smart-insights/
│   ├── inventory/
│   └── ...
│
├── static/
│   ├── css/
│   │   ├── main.css
│   │   ├── components.css
│   │   └── themes.css
│   ├── js/
│   │   ├── api-client.js          # API communication layer
│   │   ├── auth.js                # Authentication handling
│   │   ├── inventory.js           # Inventory interactions
│   │   ├── signout.js             # Sign-out interactions
│   │   └── utils.js               # Utility functions
│   ├── images/
│   │   ├── logos/
│   │   ├── icons/
│   │   └── backgrounds/
│   └── fonts/
│
└── package.json                     # If using npm for asset management
```

### 3.1 API Client (static/js/api-client.js)

```javascript
/**
 * API Client for Derivco Facilities Management System
 * Handles all backend API communications
 */

class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('access_token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Inventory Operations
    async getInventory(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/inventory?${params}`);
    }

    async getCategoryData(category) {
        return this.request(`/inventory/category/${category}`);
    }

    async getItemDetail(category, itemCode) {
        return this.request(`/inventory/item/${category}/${itemCode}`);
    }

    async getLowStockItems() {
        return this.request('/inventory/low-stock');
    }

    // Sign-Out Operations
    async getSignOutRegister() {
        return this.request('/signout/register');
    }

    async createSignOut(data) {
        return this.request('/signout/checkout', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async returnEquipment(transactionId) {
        return this.request(`/signout/return/${transactionId}`, {
            method: 'PUT'
        });
    }

    // Medical Services
    async getMedicalDashboard() {
        return this.request('/medical/dashboard');
    }

    async createIncident(data) {
        return this.request('/medical/incidents', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Analytics
    async getDashboardMetrics() {
        return this.request('/analytics/dashboard');
    }

    async getComplianceAnalysis() {
        return this.request('/analytics/compliance');
    }

    // Authentication
    async login(username, password) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (response.access_token) {
            this.token = response.access_token;
            localStorage.setItem('access_token', this.token);
        }

        return response;
    }

    logout() {
        this.token = null;
        localStorage.removeItem('access_token');
    }
}

// Global API client instance
const api = new APIClient();
```

---

## Phase 4: Migration Strategy

### Step 1: Parallel Running (Week 1-2)
- Keep Excel files operational
- Implement SQL Server database
- Populate database with current Excel data
- Run both systems in parallel

### Step 2: Data Validation (Week 3)
- Compare data between Excel and SQL Server
- Verify accuracy and completeness
- Fix any discrepancies

### Step 3: Gradual Cutover (Week 4)
- Start using SQL Server for new entries
- Keep Excel as read-only backup
- Monitor performance and stability

### Step 4: Full Migration (Week 5)
- Switch entirely to SQL Server
- Archive Excel files
- Full production deployment

### Data Migration Script

```python
"""
Data Migration Script: Excel → SQL Server
Migrates all existing data from Excel files to SQL Server
"""

import pandas as pd
from database.connection import db_manager
from database.models import (
    Category, InventoryItem, Store,
    Equipment, SignOutTransaction,
    FirstAidItem, MedicalIncident
)

def migrate_inventory_data():
    """Migrate inventory data from Excel to SQL Server"""
    print("Starting inventory migration...")

    # Load Excel data
    excel_file = 'STORES_INFRASTRUCTURE_ADMINISTRATION_enhanced.xlsx'

    with db_manager.get_session() as session:
        # Migrate categories
        categories = ['Electric', 'Plumbing', 'Carpentry', 'Painting',
                     'Aircon', 'Ceiling Tiles', 'Decoration',
                     'Parking & Signage', 'Safety', 'Access Control']

        for idx, cat_name in enumerate(categories, 1):
            category = Category(
                CategoryName=cat_name,
                DisplayOrder=idx,
                IsActive=True
            )
            session.add(category)

        session.commit()
        print(f"Migrated {len(categories)} categories")

        # Migrate inventory items for each category
        for category in categories:
            try:
                df = pd.read_excel(excel_file, sheet_name=category)

                for _, row in df.iterrows():
                    item = InventoryItem(
                        ItemCode=row.get('Item Code', ''),
                        ItemName=row.get('Description', ''),
                        CategoryID=session.query(Category).filter_by(CategoryName=category).first().CategoryID,
                        StoreID=1,  # Default store
                        CurrentStock=row.get('Quantity', 0),
                        MinimumStock=row.get('Minimum Stock', 0),
                        UnitPrice=row.get('Unit Price', 0.0),
                        Location=row.get('Location', ''),
                        IsActive=True
                    )
                    session.add(item)

                session.commit()
                print(f"Migrated items for category: {category}")

            except Exception as e:
                print(f"Error migrating {category}: {e}")
                session.rollback()

def migrate_signout_data():
    """Migrate sign-out register data"""
    print("Starting sign-out data migration...")

    excel_file = 'signout_data_improved.xlsx'
    df = pd.read_excel(excel_file)

    with db_manager.get_session() as session:
        for _, row in df.iterrows():
            transaction = SignOutTransaction(
                EquipmentID=1,  # Will need mapping logic
                EmployeeNumber=row.get('Employee Number', ''),
                EmployeeName=row.get('Employee Name', ''),
                Department=row.get('Department', ''),
                WorkOrderNumber=row.get('WO/REQ Number', ''),
                TaskDescription=row.get('Task', ''),
                SignOutDate=row.get('Sign Out Date'),
                SignInDate=row.get('Sign In Date'),
                Status='Returned' if pd.notna(row.get('Sign In Date')) else 'Checked Out'
            )
            session.add(transaction)

        session.commit()
        print(f"Migrated {len(df)} sign-out transactions")

if __name__ == '__main__':
    db_manager.initialize()
    migrate_inventory_data()
    migrate_signout_data()
    print("Migration completed successfully!")
```

---

## Phase 5: API Endpoint Design

### Inventory API Endpoints

```python
# backend/api/inventory.py

from flask import Blueprint, jsonify, request
from database.connection import db_manager
from database.models import InventoryItem, Category
from sqlalchemy import func

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')

@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    """Get all inventory items with optional filters"""
    category = request.args.get('category')
    low_stock_only = request.args.get('low_stock', 'false').lower() == 'true'

    with db_manager.get_session() as session:
        query = session.query(InventoryItem).filter_by(IsActive=True)

        if category:
            query = query.join(Category).filter(Category.CategoryName == category)

        if low_stock_only:
            query = query.filter(InventoryItem.CurrentStock <= InventoryItem.MinimumStock)

        items = query.all()

        return jsonify({
            'success': True,
            'count': len(items),
            'items': [item.to_dict() for item in items]
        })

@inventory_bp.route('/category/<category_name>', methods=['GET'])
def get_category_data(category_name):
    """Get all items in a specific category"""
    with db_manager.get_session() as session:
        items = session.query(InventoryItem).join(Category).filter(
            Category.CategoryName == category_name,
            InventoryItem.IsActive == True
        ).all()

        return jsonify({
            'success': True,
            'category': category_name,
            'count': len(items),
            'items': [item.to_dict() for item in items]
        })

@inventory_bp.route('/item/<category>/<item_code>', methods=['GET'])
def get_item_detail(category, item_code):
    """Get detailed information for a specific item"""
    with db_manager.get_session() as session:
        item = session.query(InventoryItem).filter_by(
            ItemCode=item_code,
            IsActive=True
        ).first()

        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404

        return jsonify({
            'success': True,
            'item': item.to_dict_detailed()
        })

@inventory_bp.route('/low-stock', methods=['GET'])
def get_low_stock():
    """Get all items with stock below minimum"""
    with db_manager.get_session() as session:
        items = session.query(InventoryItem).filter(
            InventoryItem.CurrentStock <= InventoryItem.MinimumStock,
            InventoryItem.IsActive == True
        ).all()

        return jsonify({
            'success': True,
            'count': len(items),
            'items': [item.to_dict() for item in items]
        })

@inventory_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard statistics"""
    with db_manager.get_session() as session:
        total_items = session.query(func.count(InventoryItem.ItemID)).filter_by(IsActive=True).scalar()
        low_stock_count = session.query(func.count(InventoryItem.ItemID)).filter(
            InventoryItem.CurrentStock <= InventoryItem.MinimumStock,
            InventoryItem.IsActive == True
        ).scalar()
        total_value = session.query(func.sum(InventoryItem.TotalValue)).filter_by(IsActive=True).scalar() or 0

        return jsonify({
            'success': True,
            'stats': {
                'total_items': total_items,
                'low_stock_count': low_stock_count,
                'total_value': float(total_value),
                'categories': session.query(func.count(Category.CategoryID)).filter_by(IsActive=True).scalar()
            }
        })
```

---

## Phase 6: Testing & Quality Assurance

### Unit Tests Example

```python
# tests/test_inventory_api.py

import pytest
from app import create_app
from database.connection import db_manager

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_get_inventory(client):
    """Test inventory listing endpoint"""
    response = client.get('/api/inventory/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'items' in data

def test_get_category_data(client):
    """Test category data endpoint"""
    response = client.get('/api/inventory/category/Electric')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['category'] == 'Electric'

def test_low_stock_items(client):
    """Test low stock items endpoint"""
    response = client.get('/api/inventory/low-stock')
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
```

---

## Phase 7: Deployment Checklist

### Pre-Deployment
- [ ] SQL Server database created and configured
- [ ] All tables and indexes created
- [ ] Migration scripts tested
- [ ] API endpoints tested
- [ ] Authentication implemented
- [ ] Error handling implemented
- [ ] Logging configured

### Deployment
- [ ] Backup current Excel files
- [ ] Run migration scripts
- [ ] Verify data integrity
- [ ] Deploy backend application
- [ ] Update frontend to use API
- [ ] Configure monitoring

### Post-Deployment
- [ ] Monitor system performance
- [ ] Check error logs
- [ ] Validate data accuracy
- [ ] User acceptance testing
- [ ] Documentation updated

---

## Benefits of This Architecture

### 1. **Scalability**
- SQL Server can handle enterprise-scale data
- API can be scaled horizontally
- Better performance with indexes

### 2. **Data Integrity**
- ACID compliance
- Foreign key constraints
- Transaction support

### 3. **Security**
- JWT authentication
- Role-based access control
- Audit trail for all operations

### 4. **Maintainability**
- Clear separation of concerns
- Easy to add new features
- Professional code structure

### 5. **Real-Time Capabilities**
- Live data updates
- Concurrent user support
- Better analytics

---

**Next Steps:**
1. Review and approve this plan
2. Set up SQL Server instance
3. Create database schema
4. Begin backend development
5. Migrate data gradually

**Estimated Timeline:** 4-6 weeks for complete migration

**Designed by:** Sifiso Cyprian Shezi
**Facilities Assistant Level 1 — Derivco Durban**
**Date:** September 30, 2025