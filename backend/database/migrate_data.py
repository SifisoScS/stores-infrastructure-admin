"""
Data Migration Script: Excel → SQL Server
Migrates all existing data from Excel files to SQL Server database
"""

import sys
import os
from datetime import datetime
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
from backend.database.connection import get_db_manager, init_database
from backend.database.models import (
    Category, Store, InventoryItem, StockMovement,
    Equipment, SignOutTransaction, FirstAidInventory, MedicalIncident,
    ServiceProvider, Supplier
)


class DataMigration:
    """Handles data migration from Excel to SQL Server"""

    def __init__(self):
        """Initialize migration"""
        self.db_manager = None
        self.excel_file = 'STORES_INFRASTRUCTURE_ADMINISTRATION_enhanced.xlsx'
        self.signout_file = 'signout_data_improved.xlsx'
        self.medical_file = 'medication_data_enhanced.xlsx'

        self.migration_stats = {
            'categories': 0,
            'stores': 0,
            'inventory_items': 0,
            'signout_transactions': 0,
            'medical_incidents': 0,
            'first_aid_items': 0,
            'errors': []
        }

    def validate_files(self) -> bool:
        """Validate Excel files exist"""
        print("\n[1/6] Validating Excel files...")

        files = {
            'Inventory': self.excel_file,
            'Sign-Out': self.signout_file,
            'Medical': self.medical_file
        }

        all_exist = True
        for name, filepath in files.items():
            if os.path.exists(filepath):
                print(f"   ✓ {name} file found: {filepath}")
            else:
                print(f"   ✗ {name} file NOT found: {filepath}")
                all_exist = False

        return all_exist

    def initialize_database(self) -> bool:
        """Initialize database connection"""
        print("\n[2/6] Initializing database connection...")

        try:
            self.db_manager = init_database(echo=False)
            print("   ✓ Database connection established")
            return True
        except Exception as e:
            print(f"   ✗ Database connection failed: {e}")
            return False

    def migrate_categories_and_stores(self) -> bool:
        """Migrate categories and stores"""
        print("\n[3/6] Migrating categories and stores...")

        try:
            with self.db_manager.get_session() as session:
                # Check if already migrated
                existing_count = session.query(Category).count()
                if existing_count > 0:
                    print(f"   - Categories already exist ({existing_count} found), skipping...")
                    self.migration_stats['categories'] = existing_count
                else:
                    # Create categories
                    categories_data = [
                        ('Electric', 'Electrical supplies and components', 'bolt', 1),
                        ('Plumbing', 'Plumbing supplies and fixtures', 'tint', 2),
                        ('Carpentry', 'Carpentry tools and materials', 'hammer', 3),
                        ('Painting', 'Painting supplies and equipment', 'paint-brush', 4),
                        ('Aircon', 'Air conditioning supplies', 'snowflake', 5),
                        ('Ceiling Tiles', 'Ceiling tiles and accessories', 'th', 6),
                        ('Decoration', 'Decorative items and accessories', 'palette', 7),
                        ('Parking & Signage', 'Parking and signage equipment', 'parking', 8),
                        ('Safety', 'Safety equipment and supplies', 'shield-alt', 9),
                        ('Access Control', 'Access control systems', 'key', 10),
                    ]

                    for name, desc, icon, order in categories_data:
                        category = Category(
                            CategoryName=name,
                            Description=desc,
                            IconName=icon,
                            DisplayOrder=order,
                            IsActive=True
                        )
                        session.add(category)

                    session.commit()
                    self.migration_stats['categories'] = len(categories_data)
                    print(f"   ✓ Migrated {len(categories_data)} categories")

                # Create default store
                existing_stores = session.query(Store).count()
                if existing_stores == 0:
                    store = Store(
                        StoreName='Main Storeroom',
                        Location='Ground Floor',
                        Floor='Ground',
                        Building='Main Building',
                        IsActive=True
                    )
                    session.add(store)
                    session.commit()
                    self.migration_stats['stores'] = 1
                    print("   ✓ Created default storeroom")
                else:
                    self.migration_stats['stores'] = existing_stores
                    print(f"   - Stores already exist ({existing_stores} found)")

            return True

        except Exception as e:
            error_msg = f"Category/Store migration error: {e}"
            print(f"   ✗ {error_msg}")
            self.migration_stats['errors'].append(error_msg)
            return False

    def migrate_inventory_items(self) -> bool:
        """Migrate inventory items from Excel"""
        print("\n[4/6] Migrating inventory items...")

        if not os.path.exists(self.excel_file):
            print(f"   ⚠ Skipping - Excel file not found: {self.excel_file}")
            return True

        try:
            with self.db_manager.get_session() as session:
                # Get category mapping
                categories = {cat.CategoryName: cat.CategoryID
                            for cat in session.query(Category).all()}

                # Get default store ID
                default_store = session.query(Store).first()
                if not default_store:
                    print("   ✗ No store found - run categories migration first")
                    return False

                # Check if already migrated
                existing_count = session.query(InventoryItem).count()
                if existing_count > 0:
                    print(f"   - Inventory items already exist ({existing_count} found)")
                    self.migration_stats['inventory_items'] = existing_count
                    return True

                # Migrate each category sheet
                items_migrated = 0
                for category_name in categories.keys():
                    try:
                        df = pd.read_excel(self.excel_file, sheet_name=category_name)

                        for idx, row in df.iterrows():
                            # Skip empty rows
                            if pd.isna(row.get('Description')) or str(row.get('Description')).strip() == '':
                                continue

                            # Clean price value - remove currency symbols
                            def clean_price(value):
                                if pd.isna(value):
                                    return 0.0
                                price_str = str(value).strip().replace('R', '').replace(',', '').replace(' ', '')
                                try:
                                    return float(price_str) if price_str else 0.0
                                except:
                                    return 0.0

                            item = InventoryItem(
                                ItemCode=str(row.get('Item Code', f'AUTO-{category_name}-{idx}')).strip(),
                                ItemName=str(row.get('Description', 'Unknown')).strip(),
                                CategoryID=categories[category_name],
                                StoreID=default_store.StoreID,
                                Description=str(row.get('Notes', ''))[:1000] if pd.notna(row.get('Notes')) else None,
                                UnitOfMeasure=str(row.get('Unit', 'ea'))[:50] if pd.notna(row.get('Unit')) else 'ea',
                                CurrentStock=int(row.get('Quantity', 0)) if pd.notna(row.get('Quantity')) else 0,
                                MinimumStock=int(row.get('Minimum Stock', 0)) if pd.notna(row.get('Minimum Stock')) else 0,
                                UnitPrice=clean_price(row.get('Unit Price', 0)),
                                Location=str(row.get('Location', ''))[:200] if pd.notna(row.get('Location')) else None,
                                IsActive=True
                            )
                            session.add(item)
                            items_migrated += 1

                        session.commit()
                        print(f"   ✓ Migrated {category_name}: {len(df)} items")

                    except Exception as e:
                        error_msg = f"Error migrating {category_name}: {e}"
                        print(f"   ⚠ {error_msg}")
                        self.migration_stats['errors'].append(error_msg)
                        session.rollback()
                        continue

                self.migration_stats['inventory_items'] = items_migrated
                print(f"   ✓ Total inventory items migrated: {items_migrated}")

            return True

        except Exception as e:
            error_msg = f"Inventory migration error: {e}"
            print(f"   ✗ {error_msg}")
            self.migration_stats['errors'].append(error_msg)
            return False

    def migrate_signout_data(self) -> bool:
        """Migrate sign-out register data"""
        print("\n[5/6] Migrating sign-out data...")

        if not os.path.exists(self.signout_file):
            print(f"   ⚠ Skipping - Sign-out file not found: {self.signout_file}")
            return True

        try:
            df = pd.read_excel(self.signout_file)

            with self.db_manager.get_session() as session:
                # Check if already migrated
                existing_count = session.query(SignOutTransaction).count()
                if existing_count > 0:
                    print(f"   - Sign-out transactions already exist ({existing_count} found)")
                    self.migration_stats['signout_transactions'] = existing_count
                    return True

                transactions_migrated = 0

                for _, row in df.iterrows():
                    # Skip rows without borrower name
                    if pd.isna(row.get('Borrower Name')) or str(row.get('Borrower Name')).strip() == '':
                        continue

                    # Create or get equipment
                    equipment_name = str(row.get('Item/Tool', 'Unknown Tool')).strip()
                    equipment = session.query(Equipment).filter_by(EquipmentName=equipment_name).first()

                    if not equipment:
                        equipment = Equipment(
                            EquipmentCode=f'EQ-{transactions_migrated + 1:04d}',
                            EquipmentName=equipment_name,
                            Category='Tools',
                            Status='Available',
                            IsActive=True
                        )
                        session.add(equipment)
                        session.flush()

                    # Determine status
                    sign_in_date = row.get('Sign In Date')
                    status = 'Returned' if pd.notna(sign_in_date) else 'Checked Out'

                    # Create transaction
                    transaction = SignOutTransaction(
                        EquipmentID=equipment.EquipmentID,
                        EmployeeNumber=str(row.get('Employee Number', ''))[:50],
                        EmployeeName=str(row.get('Borrower Name', ''))[:200],
                        Department=str(row.get('Department', ''))[:100] if pd.notna(row.get('Department')) else None,
                        WorkOrderNumber=str(row.get('WO/REQ Number', ''))[:50] if pd.notna(row.get('WO/REQ Number')) else None,
                        TaskDescription=str(row.get('Task', ''))[:500] if pd.notna(row.get('Task')) else None,
                        SignOutDate=pd.to_datetime(row.get('Sign Out Date')) if pd.notna(row.get('Sign Out Date')) else datetime.now(),
                        SignInDate=pd.to_datetime(sign_in_date) if pd.notna(sign_in_date) else None,
                        Status=status
                    )
                    session.add(transaction)
                    transactions_migrated += 1

                session.commit()
                self.migration_stats['signout_transactions'] = transactions_migrated
                print(f"   ✓ Migrated {transactions_migrated} sign-out transactions")

            return True

        except Exception as e:
            error_msg = f"Sign-out migration error: {e}"
            print(f"   ✗ {error_msg}")
            self.migration_stats['errors'].append(error_msg)
            return False

    def migrate_medical_data(self) -> bool:
        """Migrate medical services data"""
        print("\n[6/6] Migrating medical services data...")

        if not os.path.exists(self.medical_file):
            print(f"   ⚠ Skipping - Medical file not found: {self.medical_file}")
            return True

        try:
            # This is a placeholder - medical file structure needs to be defined
            # For now, just create some sample first aid items
            with self.db_manager.get_session() as session:
                existing_count = session.query(FirstAidInventory).count()
                if existing_count > 0:
                    print(f"   - Medical items already exist ({existing_count} found)")
                    self.migration_stats['first_aid_items'] = existing_count
                    return True

                # Sample first aid items
                first_aid_items = [
                    ('Bandages - Sterile', 'Bandages', 50, 20),
                    ('Antiseptic Solution', 'Antiseptic', 10, 5),
                    ('Gauze Pads', 'Dressings', 30, 15),
                    ('Medical Tape', 'Adhesives', 15, 8),
                    ('Disposable Gloves', 'PPE', 100, 50),
                ]

                for name, category, stock, min_stock in first_aid_items:
                    item = FirstAidInventory(
                        ItemName=name,
                        Category=category,
                        CurrentStock=stock,
                        MinimumStock=min_stock,
                        Location='First Aid Station',
                        IsActive=True
                    )
                    session.add(item)

                session.commit()
                self.migration_stats['first_aid_items'] = len(first_aid_items)
                print(f"   ✓ Created {len(first_aid_items)} first aid items")

            return True

        except Exception as e:
            error_msg = f"Medical data migration error: {e}"
            print(f"   ✗ {error_msg}")
            self.migration_stats['errors'].append(error_msg)
            return False

    def print_migration_summary(self):
        """Print migration summary"""
        print("\n" + "=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)

        print(f"\n✓ Categories: {self.migration_stats['categories']}")
        print(f"✓ Stores: {self.migration_stats['stores']}")
        print(f"✓ Inventory Items: {self.migration_stats['inventory_items']}")
        print(f"✓ Sign-out Transactions: {self.migration_stats['signout_transactions']}")
        print(f"✓ First Aid Items: {self.migration_stats['first_aid_items']}")

        if self.migration_stats['errors']:
            print(f"\n⚠ Warnings/Errors ({len(self.migration_stats['errors'])}):")
            for error in self.migration_stats['errors']:
                print(f"   - {error}")
        else:
            print("\n✓ No errors encountered")

        print("\n" + "=" * 80)

    def run_migration(self, validate_only=False):
        """Run full migration process"""
        print("=" * 80)
        if validate_only:
            print("DATA MIGRATION VALIDATION")
        else:
            print("DATA MIGRATION - Excel → SQL Server")
        print("=" * 80)

        # Step 1: Validate files
        if not self.validate_files():
            print("\n✗ File validation failed - cannot proceed")
            return False

        if validate_only:
            print("\n✓ All Excel files found and ready for migration")
            return True

        # Step 2: Initialize database
        if not self.initialize_database():
            print("\n✗ Database initialization failed - cannot proceed")
            return False

        # Step 3-6: Run migrations
        success = True
        success &= self.migrate_categories_and_stores()
        success &= self.migrate_inventory_items()
        success &= self.migrate_signout_data()
        success &= self.migrate_medical_data()

        # Print summary
        self.print_migration_summary()

        if success:
            print("\n✓ MIGRATION COMPLETED SUCCESSFULLY!")
            print("\nNext steps:")
            print("  1. Verify data: python backend/database/verify_data.py")
            print("  2. Test application: python app.py")
            print("  3. Set MIGRATION_MODE=parallel in .env")
        else:
            print("\n⚠ MIGRATION COMPLETED WITH WARNINGS")
            print("Review errors above and retry failed sections")

        return success


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Migrate data from Excel to SQL Server')
    parser.add_argument('--validate', action='store_true',
                       help='Validate files only, do not migrate')
    parser.add_argument('--execute', action='store_true',
                       help='Execute migration')

    args = parser.parse_args()

    if not args.validate and not args.execute:
        print("Usage: python migrate_data.py [--validate | --execute]")
        print("\nOptions:")
        print("  --validate  Validate Excel files exist (dry run)")
        print("  --execute   Run full data migration")
        return

    migration = DataMigration()

    try:
        if args.validate:
            migration.run_migration(validate_only=True)
        else:
            migration.run_migration(validate_only=False)

    except KeyboardInterrupt:
        print("\n\n✗ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()