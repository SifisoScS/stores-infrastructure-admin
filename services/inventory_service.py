#!/usr/bin/env python3
"""
Advanced Inventory Management Service for Derivco Facilities System
Implements comprehensive stock management, analytics, and automation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from pathlib import Path

# Import our Excel processor
import sys
sys.path.append('core')
from excel_processor import AdvancedExcelProcessor, ExcelProcessingError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockLevel(Enum):
    """Stock level categories for inventory management"""
    CRITICAL = "critical"      # 0-5 items
    LOW = "low"               # 6-15 items
    ADEQUATE = "adequate"     # 16-50 items
    HIGH = "high"            # 51-100 items
    OVERSTOCKED = "overstocked" # 100+ items

class AlertPriority(Enum):
    """Alert priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class InventoryItem:
    """Data class for inventory items with enhanced functionality"""
    item_code: str
    item_name: str
    category: str
    quantity: int
    unit_price: float
    total_value: float
    supplier: str
    location: str = ""
    condition: str = "Good"
    last_updated: datetime = field(default_factory=datetime.now)
    reorder_level: int = 10
    max_stock_level: int = 100
    usage_rate: float = 0.0  # Items per month

    @property
    def stock_level_category(self) -> StockLevel:
        """Determine stock level category"""
        if self.quantity <= 5:
            return StockLevel.CRITICAL
        elif self.quantity <= 15:
            return StockLevel.LOW
        elif self.quantity <= 50:
            return StockLevel.ADEQUATE
        elif self.quantity <= 100:
            return StockLevel.HIGH
        else:
            return StockLevel.OVERSTOCKED

    @property
    def days_until_stockout(self) -> Optional[int]:
        """Calculate days until stockout based on usage rate"""
        if self.usage_rate <= 0:
            return None
        return int(self.quantity / (self.usage_rate / 30))  # Convert monthly to daily rate

@dataclass
class StockAlert:
    """Data class for stock alerts"""
    alert_id: str
    item_code: str
    item_name: str
    alert_type: str
    priority: AlertPriority
    message: str
    created_at: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class AdvancedInventoryManager:
    """
    Comprehensive inventory management system with:
    - Real-time stock monitoring
    - Automated reorder alerts
    - Usage pattern analysis
    - Predictive analytics
    - Integration with sign-out system
    """

    def __init__(self, excel_processor: AdvancedExcelProcessor = None):
        self.excel_processor = excel_processor or AdvancedExcelProcessor()
        self.items: Dict[str, InventoryItem] = {}
        self.alerts: List[StockAlert] = []
        self.usage_history: Dict[str, List[Dict]] = {}
        self.audit_trail: List[Dict] = []

        # Load initial data
        self._load_inventory_data()

    def _load_inventory_data(self):
        """Load inventory data from Excel files"""
        try:
            logger.info("Loading inventory data...")

            # Read inventory data using our Excel processor
            inventory_report = self.excel_processor.generate_inventory_report()

            if 'error' in inventory_report:
                raise ExcelProcessingError(f"Failed to load inventory: {inventory_report['error']}")

            # Load items from all categories
            config = self.excel_processor.config['inventory']
            for sheet in config.sheets:
                try:
                    df = self.excel_processor.read_excel_file('inventory', sheet)
                    if not df.empty:
                        self._process_category_data(df, sheet)
                except Exception as e:
                    logger.warning(f"Could not load category {sheet}: {e}")

            logger.info(f"Loaded {len(self.items)} inventory items")

            # Generate initial alerts
            self._generate_stock_alerts()

        except Exception as e:
            logger.error(f"Error loading inventory data: {e}")
            raise

    def _process_category_data(self, df: pd.DataFrame, category: str):
        """Process inventory data for a specific category"""
        for _, row in df.iterrows():
            try:
                item = InventoryItem(
                    item_code=str(row.get('Item Code', '')),
                    item_name=str(row.get('Item Name', '')),
                    category=category,
                    quantity=int(row.get('Quantity', 0)),
                    unit_price=float(row.get('Unit Price', 0)),
                    total_value=float(row.get('Total Value', 0)),
                    supplier=str(row.get('Supplier', '')),
                    location=str(row.get('Location', '')),
                    condition=str(row.get('Condition', 'Good'))
                )

                self.items[item.item_code] = item

            except Exception as e:
                logger.warning(f"Error processing item in {category}: {e}")

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get comprehensive inventory summary"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_items': len(self.items),
            'total_value': sum(item.total_value for item in self.items.values()),
            'stock_levels': {level.value: 0 for level in StockLevel},
            'categories': {},
            'alerts': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'total': len(self.alerts)
            }
        }

        # Analyze stock levels and categories
        category_stats = {}
        for item in self.items.values():
            # Stock level distribution
            summary['stock_levels'][item.stock_level_category.value] += 1

            # Category statistics
            if item.category not in category_stats:
                category_stats[item.category] = {
                    'item_count': 0,
                    'total_value': 0,
                    'avg_price': 0,
                    'low_stock_items': 0,
                    'critical_stock_items': 0
                }

            category_stats[item.category]['item_count'] += 1
            category_stats[item.category]['total_value'] += item.total_value

            if item.stock_level_category in [StockLevel.LOW, StockLevel.CRITICAL]:
                category_stats[item.category]['low_stock_items'] += 1
            if item.stock_level_category == StockLevel.CRITICAL:
                category_stats[item.category]['critical_stock_items'] += 1

        # Calculate averages
        for cat, stats in category_stats.items():
            if stats['item_count'] > 0:
                stats['avg_price'] = stats['total_value'] / stats['item_count']

        summary['categories'] = category_stats

        # Alert distribution
        for alert in self.alerts:
            if not alert.resolved:
                summary['alerts'][alert.priority.value] += 1

        return summary

    def search_items(self, query: str, category: str = None,
                    stock_level: StockLevel = None) -> List[InventoryItem]:
        """Advanced search functionality"""
        results = []
        query_lower = query.lower()

        for item in self.items.values():
            # Text matching
            matches = (
                query_lower in item.item_name.lower() or
                query_lower in item.item_code.lower() or
                query_lower in item.supplier.lower()
            )

            # Category filter
            if category and item.category != category:
                matches = False

            # Stock level filter
            if stock_level and item.stock_level_category != stock_level:
                matches = False

            if matches:
                results.append(item)

        return sorted(results, key=lambda x: x.item_name)

    def get_low_stock_items(self, threshold: int = 15) -> List[InventoryItem]:
        """Get items with low stock levels"""
        return [
            item for item in self.items.values()
            if item.quantity <= threshold
        ]

    def get_critical_stock_items(self) -> List[InventoryItem]:
        """Get critically low stock items"""
        return [
            item for item in self.items.values()
            if item.stock_level_category == StockLevel.CRITICAL
        ]

    def predict_stockouts(self, days_ahead: int = 30) -> List[Tuple[InventoryItem, int]]:
        """Predict which items will stock out in the given timeframe"""
        predictions = []

        for item in self.items.values():
            days_until_stockout = item.days_until_stockout
            if days_until_stockout and days_until_stockout <= days_ahead:
                predictions.append((item, days_until_stockout))

        return sorted(predictions, key=lambda x: x[1])  # Sort by urgency

    def generate_reorder_recommendations(self) -> List[Dict[str, Any]]:
        """Generate intelligent reorder recommendations"""
        recommendations = []

        for item in self.items.values():
            if item.quantity <= item.reorder_level:
                # Calculate recommended order quantity
                # Using economic order quantity principles
                monthly_usage = item.usage_rate if item.usage_rate > 0 else 5  # Default assumption

                # Order enough for 2 months plus safety stock
                recommended_qty = int(monthly_usage * 2 + 10)

                # Don't exceed max stock level
                recommended_qty = min(recommended_qty, item.max_stock_level - item.quantity)

                if recommended_qty > 0:
                    recommendations.append({
                        'item_code': item.item_code,
                        'item_name': item.item_name,
                        'current_stock': item.quantity,
                        'recommended_order_qty': recommended_qty,
                        'estimated_cost': recommended_qty * item.unit_price,
                        'supplier': item.supplier,
                        'priority': 'critical' if item.quantity <= 5 else 'high',
                        'reason': f"Current stock ({item.quantity}) below reorder level ({item.reorder_level})"
                    })

        return sorted(recommendations, key=lambda x: x['current_stock'])

    def _generate_stock_alerts(self):
        """Generate stock level alerts"""
        self.alerts.clear()
        alert_count = 0

        for item in self.items.values():
            alert_id = f"STOCK_{alert_count:04d}"

            if item.stock_level_category == StockLevel.CRITICAL:
                alert = StockAlert(
                    alert_id=alert_id,
                    item_code=item.item_code,
                    item_name=item.item_name,
                    alert_type="critical_stock",
                    priority=AlertPriority.CRITICAL,
                    message=f"CRITICAL: {item.item_name} has only {item.quantity} items remaining",
                    created_at=datetime.now()
                )
                self.alerts.append(alert)
                alert_count += 1

            elif item.stock_level_category == StockLevel.LOW:
                alert = StockAlert(
                    alert_id=alert_id,
                    item_code=item.item_code,
                    item_name=item.item_name,
                    alert_type="low_stock",
                    priority=AlertPriority.HIGH,
                    message=f"LOW STOCK: {item.item_name} needs reordering ({item.quantity} remaining)",
                    created_at=datetime.now()
                )
                self.alerts.append(alert)
                alert_count += 1

            elif item.stock_level_category == StockLevel.OVERSTOCKED:
                alert = StockAlert(
                    alert_id=alert_id,
                    item_code=item.item_code,
                    item_name=item.item_name,
                    alert_type="overstocked",
                    priority=AlertPriority.MEDIUM,
                    message=f"OVERSTOCKED: {item.item_name} has excessive inventory ({item.quantity} items)",
                    created_at=datetime.now()
                )
                self.alerts.append(alert)
                alert_count += 1

    def update_stock(self, item_code: str, quantity_change: int,
                    reason: str = "", user: str = "system") -> bool:
        """Update stock levels with audit trail"""
        try:
            if item_code not in self.items:
                logger.error(f"Item {item_code} not found")
                return False

            item = self.items[item_code]
            old_quantity = item.quantity
            new_quantity = old_quantity + quantity_change

            if new_quantity < 0:
                logger.error(f"Cannot reduce stock below zero for {item_code}")
                return False

            # Update the item
            item.quantity = new_quantity
            item.total_value = new_quantity * item.unit_price
            item.last_updated = datetime.now()

            # Record in audit trail
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'item_code': item_code,
                'item_name': item.item_name,
                'action': 'stock_update',
                'old_quantity': old_quantity,
                'new_quantity': new_quantity,
                'change': quantity_change,
                'reason': reason,
                'user': user
            }
            self.audit_trail.append(audit_entry)

            # Regenerate alerts
            self._generate_stock_alerts()

            logger.info(f"Updated stock for {item_code}: {old_quantity} -> {new_quantity}")
            return True

        except Exception as e:
            logger.error(f"Error updating stock: {e}")
            return False

    def record_usage(self, item_code: str, quantity_used: int,
                    context: str = "") -> bool:
        """Record item usage for analytics"""
        try:
            if item_code not in self.usage_history:
                self.usage_history[item_code] = []

            usage_record = {
                'timestamp': datetime.now().isoformat(),
                'quantity': quantity_used,
                'context': context
            }

            self.usage_history[item_code].append(usage_record)

            # Update usage rate (monthly average)
            self._update_usage_rate(item_code)

            # Update stock level
            return self.update_stock(item_code, -quantity_used, f"Usage: {context}")

        except Exception as e:
            logger.error(f"Error recording usage: {e}")
            return False

    def _update_usage_rate(self, item_code: str):
        """Update the monthly usage rate for an item"""
        try:
            if item_code not in self.usage_history or item_code not in self.items:
                return

            history = self.usage_history[item_code]
            if not history:
                return

            # Calculate usage over the last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_usage = [
                record for record in history
                if datetime.fromisoformat(record['timestamp']) >= thirty_days_ago
            ]

            if recent_usage:
                total_usage = sum(record['quantity'] for record in recent_usage)
                self.items[item_code].usage_rate = total_usage

        except Exception as e:
            logger.warning(f"Error updating usage rate for {item_code}: {e}")

    def get_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive inventory analytics"""
        analytics = {
            'timestamp': datetime.now().isoformat(),
            'inventory_turnover': {},
            'usage_patterns': {},
            'cost_analysis': {},
            'performance_metrics': {}
        }

        try:
            # Inventory turnover analysis
            total_items = len(self.items)
            if total_items > 0:
                stock_distribution = {}
                for level in StockLevel:
                    count = sum(1 for item in self.items.values()
                              if item.stock_level_category == level)
                    stock_distribution[level.value] = {
                        'count': count,
                        'percentage': (count / total_items) * 100
                    }
                analytics['inventory_turnover'] = stock_distribution

            # Usage patterns
            high_usage_items = []
            for item_code, item in self.items.items():
                if item.usage_rate > 0:
                    high_usage_items.append({
                        'item_code': item_code,
                        'item_name': item.item_name,
                        'monthly_usage': item.usage_rate,
                        'category': item.category
                    })

            analytics['usage_patterns'] = sorted(
                high_usage_items,
                key=lambda x: x['monthly_usage'],
                reverse=True
            )[:20]  # Top 20 most used items

            # Cost analysis
            total_value = sum(item.total_value for item in self.items.values())
            category_values = {}
            for item in self.items.values():
                if item.category not in category_values:
                    category_values[item.category] = 0
                category_values[item.category] += item.total_value

            analytics['cost_analysis'] = {
                'total_inventory_value': total_value,
                'category_distribution': {
                    cat: {
                        'value': val,
                        'percentage': (val / total_value * 100) if total_value > 0 else 0
                    }
                    for cat, val in category_values.items()
                }
            }

            # Performance metrics
            analytics['performance_metrics'] = {
                'alert_count': len([a for a in self.alerts if not a.resolved]),
                'critical_items': len(self.get_critical_stock_items()),
                'items_needing_reorder': len(self.get_low_stock_items()),
                'average_stock_value_per_item': total_value / total_items if total_items > 0 else 0,
                'audit_trail_entries': len(self.audit_trail)
            }

        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            analytics['error'] = str(e)

        return analytics

    def export_inventory_report(self, file_path: str = None) -> str:
        """Export comprehensive inventory report to Excel"""
        try:
            if not file_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = f'inventory_report_{timestamp}.xlsx'

            # Prepare data for export
            inventory_data = []
            for item in self.items.values():
                inventory_data.append({
                    'Item Code': item.item_code,
                    'Item Name': item.item_name,
                    'Category': item.category,
                    'Quantity': item.quantity,
                    'Unit Price': item.unit_price,
                    'Total Value': item.total_value,
                    'Supplier': item.supplier,
                    'Stock Level': item.stock_level_category.value,
                    'Monthly Usage': item.usage_rate,
                    'Last Updated': item.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                })

            df = pd.DataFrame(inventory_data)

            # Create sheets for different analyses
            sheets = {
                'Inventory': df,
                'Low_Stock': df[df['Stock Level'].isin(['critical', 'low'])],
                'High_Value': df.nlargest(20, 'Total Value'),
                'Most_Used': df.nlargest(20, 'Monthly Usage')
            }

            # Write to Excel
            success = self.excel_processor.write_excel_file(
                sheets, file_path, 'inventory_report'
            )

            if success:
                logger.info(f"Inventory report exported to {file_path}")
                return file_path
            else:
                raise Exception("Failed to write Excel file")

        except Exception as e:
            logger.error(f"Error exporting inventory report: {e}")
            raise

    def get_audit_trail(self, item_code: str = None, days: int = 30) -> List[Dict]:
        """Get audit trail for inventory changes"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            filtered_trail = []
            for entry in self.audit_trail:
                entry_date = datetime.fromisoformat(entry['timestamp'])
                if entry_date >= cutoff_date:
                    if item_code is None or entry['item_code'] == item_code:
                        filtered_trail.append(entry)

            return sorted(filtered_trail, key=lambda x: x['timestamp'], reverse=True)

        except Exception as e:
            logger.error(f"Error retrieving audit trail: {e}")
            return []