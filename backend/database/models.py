"""
SQLAlchemy ORM Models for Derivco Facilities Management System
All database tables mapped to Python classes
"""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Numeric, Date,
    ForeignKey, Text, Index, CheckConstraint, func, text
)
from sqlalchemy.orm import relationship, backref

from .base import Base, BaseModel


# ============================================================================
# INVENTORY MANAGEMENT MODELS
# ============================================================================

class Category(Base, BaseModel):
    """Inventory categories (Electric, Plumbing, Carpentry, etc.)"""

    __tablename__ = 'Categories'

    CategoryID = Column(Integer, primary_key=True, autoincrement=True)
    CategoryName = Column(String(100), nullable=False, unique=True)
    Description = Column(String(500))
    IconName = Column(String(50))
    DisplayOrder = Column(Integer)
    IsActive = Column(Boolean, default=True, nullable=False)
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    ModifiedDate = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    items = relationship('InventoryItem', back_populates='category', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Category(id={self.CategoryID}, name='{self.CategoryName}')>"


class Store(Base, BaseModel):
    """Stores/Locations/Storerooms"""

    __tablename__ = 'Stores'

    StoreID = Column(Integer, primary_key=True, autoincrement=True)
    StoreName = Column(String(100), nullable=False)
    Location = Column(String(200))
    Floor = Column(String(50))
    Building = Column(String(100))
    IsActive = Column(Boolean, default=True, nullable=False)
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    items = relationship('InventoryItem', back_populates='store')

    def __repr__(self):
        return f"<Store(id={self.StoreID}, name='{self.StoreName}')>"


class InventoryItem(Base, BaseModel):
    """Inventory items with stock tracking"""

    __tablename__ = 'InventoryItems'

    ItemID = Column(Integer, primary_key=True, autoincrement=True)
    ItemCode = Column(String(50), nullable=False, unique=True, index=True)
    ItemName = Column(String(200), nullable=False)
    CategoryID = Column(Integer, ForeignKey('Categories.CategoryID'), nullable=False, index=True)
    StoreID = Column(Integer, ForeignKey('Stores.StoreID'), nullable=False, index=True)
    Description = Column(String(1000))
    UnitOfMeasure = Column(String(50))
    CurrentStock = Column(Integer, default=0, nullable=False)
    MinimumStock = Column(Integer, default=0, nullable=False)
    MaximumStock = Column(Integer)
    UnitPrice = Column(Numeric(10, 2))
    # TotalValue will be computed: CurrentStock * UnitPrice
    Location = Column(String(200))
    Supplier = Column(String(200))
    LastRestockDate = Column(Date)
    IsActive = Column(Boolean, default=True, nullable=False)
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    ModifiedDate = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    category = relationship('Category', back_populates='items')
    store = relationship('Store', back_populates='items')
    stock_movements = relationship('StockMovement', back_populates='item', cascade='all, delete-orphan')

    # Indexes for performance
    __table_args__ = (
        Index('idx_items_low_stock', 'CurrentStock', 'MinimumStock'),
        CheckConstraint('CurrentStock >= 0', name='chk_current_stock_positive'),
    )

    @property
    def total_value(self):
        """Calculate total value of stock"""
        if self.CurrentStock and self.UnitPrice:
            return float(self.CurrentStock * self.UnitPrice)
        return 0.0

    @property
    def is_low_stock(self):
        """Check if item is low on stock"""
        return self.CurrentStock <= self.MinimumStock

    def __repr__(self):
        return f"<InventoryItem(id={self.ItemID}, code='{self.ItemCode}', name='{self.ItemName}')>"


class StockMovement(Base, BaseModel):
    """Stock movement history (IN, OUT, ADJUSTMENT, TRANSFER)"""

    __tablename__ = 'StockMovements'

    MovementID = Column(Integer, primary_key=True, autoincrement=True)
    ItemID = Column(Integer, ForeignKey('InventoryItems.ItemID'), nullable=False, index=True)
    MovementType = Column(String(50), nullable=False)  # 'IN', 'OUT', 'ADJUSTMENT', 'TRANSFER'
    Quantity = Column(Integer, nullable=False)
    PreviousStock = Column(Integer)
    NewStock = Column(Integer)
    Reference = Column(String(100))  # Work Order, REQ number, etc.
    Notes = Column(String(500))
    CreatedBy = Column(String(100))
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    item = relationship('InventoryItem', back_populates='stock_movements')

    def __repr__(self):
        return f"<StockMovement(id={self.MovementID}, type='{self.MovementType}', qty={self.Quantity})>"


# ============================================================================
# SIGN-OUT REGISTER MODELS
# ============================================================================

class Equipment(Base, BaseModel):
    """Equipment/Tools available for sign-out"""

    __tablename__ = 'Equipment'

    EquipmentID = Column(Integer, primary_key=True, autoincrement=True)
    EquipmentCode = Column(String(50), nullable=False, unique=True, index=True)
    EquipmentName = Column(String(200), nullable=False)
    Category = Column(String(100))
    Description = Column(String(500))
    SerialNumber = Column(String(100))
    PurchaseDate = Column(Date)
    Value = Column(Numeric(10, 2))
    Status = Column(String(50), default='Available')  # 'Available', 'Checked Out', 'Maintenance', 'Lost'
    IsActive = Column(Boolean, default=True, nullable=False)
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    transactions = relationship('SignOutTransaction', back_populates='equipment')

    def __repr__(self):
        return f"<Equipment(id={self.EquipmentID}, code='{self.EquipmentCode}', name='{self.EquipmentName}')>"


class SignOutTransaction(Base, BaseModel):
    """Sign-out transaction records"""

    __tablename__ = 'SignOutTransactions'

    TransactionID = Column(Integer, primary_key=True, autoincrement=True)
    EquipmentID = Column(Integer, ForeignKey('Equipment.EquipmentID'), nullable=False, index=True)
    EmployeeNumber = Column(String(50), nullable=False, index=True)
    EmployeeName = Column(String(200), nullable=False)
    Department = Column(String(100))
    WorkOrderNumber = Column(String(50), index=True)  # REQ/WO Number
    TaskDescription = Column(String(500))
    SignOutDate = Column(DateTime, nullable=False, index=True)
    ExpectedReturnDate = Column(Date)
    SignInDate = Column(DateTime)
    Status = Column(String(50), default='Checked Out', index=True)  # 'Checked Out', 'Returned', 'Overdue', 'Lost'
    SignOutBy = Column(String(100))  # Who issued it
    SignInBy = Column(String(100))  # Who received it back
    Notes = Column(String(500))
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    ModifiedDate = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    equipment = relationship('Equipment', back_populates='transactions')

    # Indexes for overdue checking
    __table_args__ = (
        Index('idx_signout_overdue', 'ExpectedReturnDate', 'Status'),
    )

    @property
    def is_overdue(self):
        """Check if item is overdue"""
        if self.Status == 'Checked Out' and self.ExpectedReturnDate:
            return date.today() > self.ExpectedReturnDate
        return False

    def __repr__(self):
        return f"<SignOutTransaction(id={self.TransactionID}, employee='{self.EmployeeName}', status='{self.Status}')>"


# ============================================================================
# MEDICAL SERVICES MODELS
# ============================================================================

class FirstAidInventory(Base, BaseModel):
    """First aid kit inventory items"""

    __tablename__ = 'FirstAidInventory'

    ItemID = Column(Integer, primary_key=True, autoincrement=True)
    ItemName = Column(String(200), nullable=False)
    Category = Column(String(100))
    CurrentStock = Column(Integer, default=0, nullable=False)
    MinimumStock = Column(Integer, default=0, nullable=False)
    ExpiryDate = Column(Date)
    Location = Column(String(200))
    Supplier = Column(String(200))
    LastRestockDate = Column(Date)
    IsActive = Column(Boolean, default=True, nullable=False)
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)

    @property
    def is_low_stock(self):
        """Check if item is low on stock"""
        return self.CurrentStock <= self.MinimumStock

    @property
    def is_expired(self):
        """Check if item is expired"""
        if self.ExpiryDate:
            return date.today() > self.ExpiryDate
        return False

    def __repr__(self):
        return f"<FirstAidInventory(id={self.ItemID}, name='{self.ItemName}')>"


class MedicalIncident(Base, BaseModel):
    """Medical incidents and treatment records"""

    __tablename__ = 'MedicalIncidents'

    IncidentID = Column(Integer, primary_key=True, autoincrement=True)
    IncidentDate = Column(DateTime, nullable=False, index=True)
    EmployeeNumber = Column(String(50))
    EmployeeName = Column(String(200))
    IncidentType = Column(String(100))  # 'Injury', 'Illness', 'First Aid', 'Emergency'
    Severity = Column(String(50))  # 'Minor', 'Moderate', 'Severe', 'Critical'
    Description = Column(Text)
    TreatmentGiven = Column(Text)
    Location = Column(String(200))
    WitnessName = Column(String(200))
    ReportedBy = Column(String(100))
    FollowUpRequired = Column(Boolean, default=False)
    FollowUpDate = Column(Date)
    Status = Column(String(50), default='Open', index=True)  # 'Open', 'Under Investigation', 'Closed'
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    ModifiedDate = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<MedicalIncident(id={self.IncidentID}, type='{self.IncidentType}', severity='{self.Severity}')>"


# ============================================================================
# SERVICE PROVIDERS MODELS
# ============================================================================

class ServiceProvider(Base, BaseModel):
    """External service providers and contractors"""

    __tablename__ = 'ServiceProviders'

    ProviderID = Column(Integer, primary_key=True, autoincrement=True)
    ProviderCode = Column(String(50), nullable=False, unique=True)
    ProviderName = Column(String(200), nullable=False)
    ServiceType = Column(String(100))  # 'Catering', 'Cleaning', 'Garden', 'Maintenance'
    ContactPerson = Column(String(200))
    Email = Column(String(200))
    Phone = Column(String(50))
    Address = Column(String(500))
    ContractStartDate = Column(Date)
    ContractEndDate = Column(Date)
    ContractValue = Column(Numeric(15, 2))
    PerformanceRating = Column(Numeric(3, 2))  # 1.00 to 5.00
    IsActive = Column(Boolean, default=True, nullable=False)
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    ModifiedDate = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    metrics = relationship('ServiceMetric', back_populates='provider', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<ServiceProvider(id={self.ProviderID}, name='{self.ProviderName}')>"


class ServiceMetric(Base, BaseModel):
    """Service provider performance metrics"""

    __tablename__ = 'ServiceMetrics'

    MetricID = Column(Integer, primary_key=True, autoincrement=True)
    ProviderID = Column(Integer, ForeignKey('ServiceProviders.ProviderID'), nullable=False)
    MetricDate = Column(Date, nullable=False)
    ServiceQuality = Column(Numeric(3, 2))
    ResponseTime = Column(Integer)  # in minutes
    ComplianceScore = Column(Numeric(5, 2))
    CustomerSatisfaction = Column(Numeric(3, 2))
    Notes = Column(String(500))
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    provider = relationship('ServiceProvider', back_populates='metrics')

    def __repr__(self):
        return f"<ServiceMetric(id={self.MetricID}, provider_id={self.ProviderID}, date={self.MetricDate})>"


# ============================================================================
# FACILITIES MANAGEMENT MODELS
# ============================================================================

class MaintenanceLog(Base, BaseModel):
    """Maintenance work orders and logs"""

    __tablename__ = 'MaintenanceLog'

    LogID = Column(Integer, primary_key=True, autoincrement=True)
    WorkOrderNumber = Column(String(50), nullable=False, index=True)
    REQNumber = Column(String(50))
    AssetType = Column(String(100))
    AssetLocation = Column(String(200))
    IssueDescription = Column(Text)
    Priority = Column(String(50), index=True)  # 'Low', 'Medium', 'High', 'Critical'
    AssignedTo = Column(String(100))
    Status = Column(String(50), index=True)  # 'Pending', 'In Progress', 'Completed', 'Cancelled'
    RequestedDate = Column(DateTime)
    StartDate = Column(DateTime)
    CompletedDate = Column(DateTime)
    TotalCost = Column(Numeric(10, 2))
    Notes = Column(Text)
    CreatedBy = Column(String(100))
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    ModifiedDate = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<MaintenanceLog(id={self.LogID}, wo='{self.WorkOrderNumber}', status='{self.Status}')>"


class Supplier(Base, BaseModel):
    """Suppliers and contractors"""

    __tablename__ = 'Suppliers'

    SupplierID = Column(Integer, primary_key=True, autoincrement=True)
    SupplierName = Column(String(200), nullable=False)
    SupplierType = Column(String(100))  # 'Supplier', 'Contractor', 'Vendor'
    Category = Column(String(100))
    ContactPerson = Column(String(200))
    Email = Column(String(200))
    Phone = Column(String(50))
    Address = Column(String(500))
    TaxNumber = Column(String(50))
    BankDetails = Column(String(500))
    Rating = Column(Numeric(3, 2))
    IsActive = Column(Boolean, default=True, nullable=False)
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Supplier(id={self.SupplierID}, name='{self.SupplierName}')>"


# ============================================================================
# USER MANAGEMENT & SECURITY MODELS
# ============================================================================

class User(Base, BaseModel):
    """System users with authentication"""

    __tablename__ = 'Users'

    UserID = Column(Integer, primary_key=True, autoincrement=True)
    EmployeeNumber = Column(String(50), nullable=False, unique=True)
    Username = Column(String(100), nullable=False, unique=True, index=True)
    PasswordHash = Column(String(500), nullable=False)
    FirstName = Column(String(100))
    LastName = Column(String(100))
    Email = Column(String(200), unique=True)
    Phone = Column(String(50))
    Department = Column(String(100))
    JobTitle = Column(String(100))
    Role = Column(String(50), nullable=False, default='User')  # 'Admin', 'Manager', 'Assistant', 'User'
    IsActive = Column(Boolean, default=True, nullable=False)
    LastLogin = Column(DateTime)
    CreatedDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    ModifiedDate = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    audit_logs = relationship('AuditLog', back_populates='user')

    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.FirstName} {self.LastName}".strip()

    def __repr__(self):
        return f"<User(id={self.UserID}, username='{self.Username}', role='{self.Role}')>"


class AuditLog(Base, BaseModel):
    """Audit trail for all system operations"""

    __tablename__ = 'AuditLog'

    AuditID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('Users.UserID'))
    ActionType = Column(String(100), nullable=False)  # 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'EXPORT'
    TableName = Column(String(100))
    RecordID = Column(Integer)
    OldValue = Column(Text)
    NewValue = Column(Text)
    IPAddress = Column(String(50))
    Timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship('User', back_populates='audit_logs')

    def __repr__(self):
        return f"<AuditLog(id={self.AuditID}, action='{self.ActionType}', table='{self.TableName}')>"


# ============================================================================
# HELPER FUNCTION TO CREATE ALL TABLES
# ============================================================================

def create_all_tables(engine):
    """
    Create all database tables

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)
    print("✓ All database tables created successfully")


def drop_all_tables(engine):
    """
    Drop all database tables (USE WITH CAUTION!)

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(engine)
    print("✓ All database tables dropped")