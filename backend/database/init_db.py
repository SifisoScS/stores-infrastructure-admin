"""
Database Initialization Script
Creates all tables and indexes in SQL Server database
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database.connection import init_database
from backend.database.models import (
    Base, Category, Store, InventoryItem, StockMovement,
    Equipment, SignOutTransaction, FirstAidInventory, MedicalIncident,
    ServiceProvider, ServiceMetric, MaintenanceLog, Supplier,
    User, AuditLog
)
from sqlalchemy import text


def create_database_schema():
    """Create all database tables and indexes"""

    print("=" * 80)
    print("DATABASE INITIALIZATION - Derivco Facilities Management")
    print("=" * 80)

    try:
        # Initialize database connection
        print("\n[1/4] Initializing database connection...")
        db_manager = init_database(echo=False)

        # Create all tables
        print("\n[2/4] Creating database tables...")
        Base.metadata.create_all(db_manager.engine)

        # Verify tables were created
        print("\n[3/4] Verifying tables...")
        with db_manager.get_session() as session:
            result = session.execute(text("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))
            tables = [row[0] for row in result.fetchall()]

            print(f"\n   Created {len(tables)} tables:")
            for table in tables:
                print(f"   ✓ {table}")

        # Create additional indexes if needed
        print("\n[4/4] Creating additional indexes...")
        create_additional_indexes(db_manager.engine)

        print("\n" + "=" * 80)
        print("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n✓ All tables and indexes created")
        print("✓ Database ready for data migration")
        print("\nNext steps:")
        print("  1. Run data migration: python backend/database/migrate_data.py")
        print("  2. Verify data: python backend/database/verify_data.py")
        print("  3. Start application: python app.py")

    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check .env file exists with correct SQL Server credentials")
        print("  2. Verify SQL Server is running and accessible")
        print("  3. Ensure database 'DerivcoDurbanFacilities' exists")
        print("  4. Check firewall allows SQL Server connections")
        raise


def create_additional_indexes(engine):
    """Create additional indexes for performance"""

    indexes = [
        # Inventory items - frequently queried fields
        "CREATE NONCLUSTERED INDEX IX_Items_CategoryStore ON InventoryItems(CategoryID, StoreID) WHERE IsActive = 1",

        # Sign-out transactions - overdue checking
        "CREATE NONCLUSTERED INDEX IX_SignOut_EmployeeStatus ON SignOutTransactions(EmployeeNumber, Status) WHERE Status = 'Checked Out'",

        # Medical incidents - date range queries
        "CREATE NONCLUSTERED INDEX IX_Incidents_DateStatus ON MedicalIncidents(IncidentDate DESC, Status)",

        # Maintenance log - priority and status
        "CREATE NONCLUSTERED INDEX IX_Maintenance_PriorityStatus ON MaintenanceLog(Priority, Status) WHERE Status != 'Completed'",

        # Audit log - user activity tracking
        "CREATE NONCLUSTERED INDEX IX_Audit_UserTimestamp ON AuditLog(UserID, Timestamp DESC)",
    ]

    with engine.connect() as conn:
        for idx_sql in indexes:
            try:
                # Check if index already exists
                index_name = idx_sql.split()[2]  # Extract index name
                check_sql = text(f"""
                    SELECT COUNT(*) as cnt
                    FROM sys.indexes
                    WHERE name = :index_name
                """)
                result = conn.execute(check_sql, {"index_name": index_name})
                if result.fetchone()[0] == 0:
                    conn.execute(text(idx_sql))
                    print(f"   ✓ Created index: {index_name}")
                else:
                    print(f"   - Index already exists: {index_name}")
                conn.commit()
            except Exception as e:
                print(f"   ⚠ Warning: Could not create index: {e}")
                continue


def seed_initial_data():
    """Seed database with initial data (categories, default user, etc.)"""

    print("\n" + "=" * 80)
    print("SEEDING INITIAL DATA")
    print("=" * 80)

    from backend.database.connection import get_db_manager

    db_manager = get_db_manager()

    with db_manager.get_session() as session:
        # Check if categories already exist
        existing_count = session.query(Category).count()
        if existing_count > 0:
            print(f"\n✓ Categories already exist ({existing_count} found)")
            return

        # Create default categories
        categories = [
            Category(CategoryName='Electric', Description='Electrical supplies and components',
                    IconName='bolt', DisplayOrder=1),
            Category(CategoryName='Plumbing', Description='Plumbing supplies and fixtures',
                    IconName='tint', DisplayOrder=2),
            Category(CategoryName='Carpentry', Description='Carpentry tools and materials',
                    IconName='hammer', DisplayOrder=3),
            Category(CategoryName='Painting', Description='Painting supplies and equipment',
                    IconName='paint-brush', DisplayOrder=4),
            Category(CategoryName='Aircon', Description='Air conditioning supplies',
                    IconName='snowflake', DisplayOrder=5),
            Category(CategoryName='Ceiling Tiles', Description='Ceiling tiles and accessories',
                    IconName='th', DisplayOrder=6),
            Category(CategoryName='Decoration', Description='Decorative items and accessories',
                    IconName='palette', DisplayOrder=7),
            Category(CategoryName='Parking & Signage', Description='Parking and signage equipment',
                    IconName='parking', DisplayOrder=8),
            Category(CategoryName='Safety', Description='Safety equipment and supplies',
                    IconName='shield-alt', DisplayOrder=9),
            Category(CategoryName='Access Control', Description='Access control systems',
                    IconName='key', DisplayOrder=10),
        ]

        for category in categories:
            session.add(category)

        # Create default store/storeroom
        store = Store(
            StoreName='Main Storeroom',
            Location='Ground Floor',
            Floor='Ground',
            Building='Main Building'
        )
        session.add(store)

        session.commit()

        print(f"\n✓ Created {len(categories)} default categories")
        print("✓ Created default storeroom")


def verify_database_setup():
    """Verify database is set up correctly"""

    print("\n" + "=" * 80)
    print("VERIFYING DATABASE SETUP")
    print("=" * 80)

    from backend.database.connection import get_db_manager

    db_manager = get_db_manager()

    with db_manager.get_session() as session:
        # Check table counts
        checks = [
            ("Categories", Category),
            ("Stores", Store),
            ("InventoryItems", InventoryItem),
            ("Equipment", Equipment),
            ("Users", User),
        ]

        print("\nTable Status:")
        all_good = True
        for table_name, model in checks:
            try:
                count = session.query(model).count()
                status = "✓" if count >= 0 else "✗"
                print(f"   {status} {table_name}: {count} records")
            except Exception as e:
                print(f"   ✗ {table_name}: Error - {e}")
                all_good = False

        if all_good:
            print("\n✓ Database verification passed!")
        else:
            print("\n⚠ Some issues detected - review errors above")

        return all_good


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Initialize Derivco Facilities Management Database')
    parser.add_argument('--seed', action='store_true', help='Seed initial data after creating tables')
    parser.add_argument('--verify', action='store_true', help='Verify database setup')
    args = parser.parse_args()

    try:
        # Create database schema
        create_database_schema()

        # Seed initial data if requested
        if args.seed:
            seed_initial_data()

        # Verify setup if requested
        if args.verify:
            verify_database_setup()

    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)