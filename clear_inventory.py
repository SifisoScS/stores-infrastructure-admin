"""
Clear inventory items to allow re-migration
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.database.connection import init_database
from sqlalchemy import text

# Initialize database
db = init_database()

# Clear inventory items
with db.get_session() as session:
    result = session.execute(text('DELETE FROM InventoryItems'))
    print(f"Deleted {result.rowcount} inventory items")

print("Ready for re-migration. Run: python backend/database/migrate_data.py --execute")