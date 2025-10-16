#!/usr/bin/env python3
"""
REST API endpoints for Derivco Facilities Inventory Management
Provides comprehensive API access to all inventory operations
"""

from flask import Blueprint, jsonify, request, current_app
from flask_cors import cross_origin
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import json

# Import our services
import sys
sys.path.append('core')
sys.path.append('services')
from excel_processor import AdvancedExcelProcessor
from inventory_service import AdvancedInventoryManager, StockLevel, AlertPriority

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint for inventory API
inventory_api = Blueprint('inventory_api', __name__, url_prefix='/api/inventory')

# Global instances (will be initialized in main app)
excel_processor = None
inventory_manager = None

def init_api(excel_proc, inv_manager):
    """Initialize API with service instances"""
    global excel_processor, inventory_manager
    excel_processor = excel_proc
    inventory_manager = inv_manager

def create_response(data: Any = None, message: str = "", status: int = 200,
                   success: bool = True) -> tuple:
    """Create standardized API response"""
    response = {
        'success': success,
        'timestamp': datetime.now().isoformat(),
        'message': message
    }

    if data is not None:
        response['data'] = data

    return jsonify(response), status

def handle_api_error(e: Exception, message: str = "An error occurred") -> tuple:
    """Handle API errors consistently"""
    logger.error(f"API Error: {e}")
    return create_response(
        data={'error': str(e)},
        message=message,
        status=500,
        success=False
    )

# ==============================================================================
# INVENTORY OVERVIEW ENDPOINTS
# ==============================================================================

@inventory_api.route('/summary', methods=['GET'])
@cross_origin()
def get_inventory_summary():
    """
    GET /api/inventory/summary
    Returns comprehensive inventory summary with statistics
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        summary = inventory_manager.get_inventory_summary()
        return create_response(
            data=summary,
            message="Inventory summary retrieved successfully"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to retrieve inventory summary")

@inventory_api.route('/analytics', methods=['GET'])
@cross_origin()
def get_inventory_analytics():
    """
    GET /api/inventory/analytics
    Returns advanced inventory analytics and insights
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        analytics = inventory_manager.get_analytics()
        return create_response(
            data=analytics,
            message="Inventory analytics retrieved successfully"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to retrieve inventory analytics")

@inventory_api.route('/categories', methods=['GET'])
@cross_origin()
def get_categories():
    """
    GET /api/inventory/categories
    Returns all inventory categories with their statistics
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        summary = inventory_manager.get_inventory_summary()
        categories = summary.get('categories', {})

        return create_response(
            data={
                'categories': categories,
                'total_categories': len(categories)
            },
            message="Categories retrieved successfully"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to retrieve categories")

# ==============================================================================
# ITEM MANAGEMENT ENDPOINTS
# ==============================================================================

@inventory_api.route('/items', methods=['GET'])
@cross_origin()
def get_all_items():
    """
    GET /api/inventory/items?category=&stock_level=&page=&per_page=
    Returns paginated list of inventory items with filtering
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        # Get query parameters
        category = request.args.get('category')
        stock_level = request.args.get('stock_level')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)  # Max 100 items per page

        # Get all items
        all_items = list(inventory_manager.items.values())

        # Apply filters
        filtered_items = []
        for item in all_items:
            if category and item.category != category:
                continue
            if stock_level and item.stock_level_category.value != stock_level:
                continue
            filtered_items.append(item)

        # Pagination
        total_items = len(filtered_items)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_items = filtered_items[start_idx:end_idx]

        # Convert to dict format
        items_data = []
        for item in paginated_items:
            items_data.append({
                'item_code': item.item_code,
                'item_name': item.item_name,
                'category': item.category,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_value': item.total_value,
                'supplier': item.supplier,
                'location': item.location,
                'condition': item.condition,
                'stock_level': item.stock_level_category.value,
                'reorder_level': item.reorder_level,
                'usage_rate': item.usage_rate,
                'days_until_stockout': item.days_until_stockout,
                'last_updated': item.last_updated.isoformat()
            })

        return create_response(
            data={
                'items': items_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_items,
                    'pages': (total_items + per_page - 1) // per_page
                },
                'filters': {
                    'category': category,
                    'stock_level': stock_level
                }
            },
            message=f"Retrieved {len(items_data)} items"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to retrieve items")

@inventory_api.route('/items/<item_code>', methods=['GET'])
@cross_origin()
def get_item_details(item_code: str):
    """
    GET /api/inventory/items/<item_code>
    Returns detailed information for a specific item
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        if item_code not in inventory_manager.items:
            return create_response(
                message=f"Item {item_code} not found",
                status=404,
                success=False
            )

        item = inventory_manager.items[item_code]

        # Get usage history
        usage_history = inventory_manager.usage_history.get(item_code, [])
        recent_usage = usage_history[-10:]  # Last 10 usage records

        # Get audit trail
        audit_trail = inventory_manager.get_audit_trail(item_code, days=30)

        item_data = {
            'item_code': item.item_code,
            'item_name': item.item_name,
            'category': item.category,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'total_value': item.total_value,
            'supplier': item.supplier,
            'location': item.location,
            'condition': item.condition,
            'stock_level': item.stock_level_category.value,
            'reorder_level': item.reorder_level,
            'max_stock_level': item.max_stock_level,
            'usage_rate': item.usage_rate,
            'days_until_stockout': item.days_until_stockout,
            'last_updated': item.last_updated.isoformat(),
            'usage_history': recent_usage,
            'audit_trail': audit_trail
        }

        return create_response(
            data=item_data,
            message=f"Item details retrieved for {item_code}"
        )

    except Exception as e:
        return handle_api_error(e, f"Failed to retrieve item {item_code}")

@inventory_api.route('/search', methods=['GET'])
@cross_origin()
def search_items():
    """
    GET /api/inventory/search?q=&category=&stock_level=
    Search inventory items by query string
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        query = request.args.get('q', '').strip()
        category = request.args.get('category')
        stock_level_str = request.args.get('stock_level')

        if not query:
            return create_response(
                message="Search query is required",
                status=400,
                success=False
            )

        # Convert stock level string to enum if provided
        stock_level = None
        if stock_level_str:
            try:
                stock_level = StockLevel(stock_level_str)
            except ValueError:
                return create_response(
                    message=f"Invalid stock level: {stock_level_str}",
                    status=400,
                    success=False
                )

        # Perform search
        results = inventory_manager.search_items(query, category, stock_level)

        # Convert results to dict format
        search_results = []
        for item in results:
            search_results.append({
                'item_code': item.item_code,
                'item_name': item.item_name,
                'category': item.category,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_value': item.total_value,
                'supplier': item.supplier,
                'stock_level': item.stock_level_category.value
            })

        return create_response(
            data={
                'query': query,
                'results': search_results,
                'count': len(search_results)
            },
            message=f"Found {len(search_results)} items matching '{query}'"
        )

    except Exception as e:
        return handle_api_error(e, "Search failed")

# ==============================================================================
# STOCK MANAGEMENT ENDPOINTS
# ==============================================================================

@inventory_api.route('/stock/update', methods=['POST'])
@cross_origin()
def update_stock():
    """
    POST /api/inventory/stock/update
    Update stock levels for items
    Body: {
        "item_code": "string",
        "quantity_change": integer,
        "reason": "string",
        "user": "string"
    }
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        data = request.get_json()
        if not data:
            return create_response(
                message="Request body is required",
                status=400,
                success=False
            )

        # Validate required fields
        required_fields = ['item_code', 'quantity_change']
        for field in required_fields:
            if field not in data:
                return create_response(
                    message=f"Field '{field}' is required",
                    status=400,
                    success=False
                )

        item_code = data['item_code']
        quantity_change = int(data['quantity_change'])
        reason = data.get('reason', 'API update')
        user = data.get('user', 'api_user')

        # Update stock
        success = inventory_manager.update_stock(item_code, quantity_change, reason, user)

        if success:
            updated_item = inventory_manager.items[item_code]
            return create_response(
                data={
                    'item_code': item_code,
                    'new_quantity': updated_item.quantity,
                    'stock_level': updated_item.stock_level_category.value
                },
                message=f"Stock updated successfully for {item_code}"
            )
        else:
            return create_response(
                message=f"Failed to update stock for {item_code}",
                status=400,
                success=False
            )

    except Exception as e:
        return handle_api_error(e, "Failed to update stock")

@inventory_api.route('/stock/low', methods=['GET'])
@cross_origin()
def get_low_stock_items():
    """
    GET /api/inventory/stock/low?threshold=
    Returns items with low stock levels
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        threshold = int(request.args.get('threshold', 15))
        low_stock_items = inventory_manager.get_low_stock_items(threshold)

        items_data = []
        for item in low_stock_items:
            items_data.append({
                'item_code': item.item_code,
                'item_name': item.item_name,
                'category': item.category,
                'quantity': item.quantity,
                'reorder_level': item.reorder_level,
                'stock_level': item.stock_level_category.value,
                'supplier': item.supplier,
                'unit_price': item.unit_price
            })

        return create_response(
            data={
                'threshold': threshold,
                'items': items_data,
                'count': len(items_data)
            },
            message=f"Found {len(items_data)} low stock items"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to retrieve low stock items")

@inventory_api.route('/stock/critical', methods=['GET'])
@cross_origin()
def get_critical_stock_items():
    """
    GET /api/inventory/stock/critical
    Returns critically low stock items
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        critical_items = inventory_manager.get_critical_stock_items()

        items_data = []
        for item in critical_items:
            items_data.append({
                'item_code': item.item_code,
                'item_name': item.item_name,
                'category': item.category,
                'quantity': item.quantity,
                'reorder_level': item.reorder_level,
                'supplier': item.supplier,
                'unit_price': item.unit_price
            })

        return create_response(
            data={
                'items': items_data,
                'count': len(items_data)
            },
            message=f"Found {len(items_data)} critical stock items"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to retrieve critical stock items")

# ==============================================================================
# ALERTS AND RECOMMENDATIONS
# ==============================================================================

@inventory_api.route('/alerts', methods=['GET'])
@cross_origin()
def get_alerts():
    """
    GET /api/inventory/alerts?resolved=&priority=
    Returns inventory alerts
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        show_resolved = request.args.get('resolved', 'false').lower() == 'true'
        priority_filter = request.args.get('priority')

        alerts = inventory_manager.alerts

        # Filter alerts
        filtered_alerts = []
        for alert in alerts:
            if not show_resolved and alert.resolved:
                continue
            if priority_filter and alert.priority.value != priority_filter:
                continue
            filtered_alerts.append(alert)

        # Convert to dict format
        alerts_data = []
        for alert in filtered_alerts:
            alerts_data.append({
                'alert_id': alert.alert_id,
                'item_code': alert.item_code,
                'item_name': alert.item_name,
                'alert_type': alert.alert_type,
                'priority': alert.priority.value,
                'message': alert.message,
                'created_at': alert.created_at.isoformat(),
                'resolved': alert.resolved,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
            })

        return create_response(
            data={
                'alerts': alerts_data,
                'count': len(alerts_data),
                'filters': {
                    'show_resolved': show_resolved,
                    'priority': priority_filter
                }
            },
            message=f"Retrieved {len(alerts_data)} alerts"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to retrieve alerts")

@inventory_api.route('/recommendations/reorder', methods=['GET'])
@cross_origin()
def get_reorder_recommendations():
    """
    GET /api/inventory/recommendations/reorder
    Returns intelligent reorder recommendations
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        recommendations = inventory_manager.generate_reorder_recommendations()

        return create_response(
            data={
                'recommendations': recommendations,
                'count': len(recommendations)
            },
            message=f"Generated {len(recommendations)} reorder recommendations"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to generate reorder recommendations")

@inventory_api.route('/predictions/stockout', methods=['GET'])
@cross_origin()
def predict_stockouts():
    """
    GET /api/inventory/predictions/stockout?days=
    Predict upcoming stockouts
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        days_ahead = int(request.args.get('days', 30))
        predictions = inventory_manager.predict_stockouts(days_ahead)

        predictions_data = []
        for item, days_until_stockout in predictions:
            predictions_data.append({
                'item_code': item.item_code,
                'item_name': item.item_name,
                'category': item.category,
                'current_quantity': item.quantity,
                'usage_rate': item.usage_rate,
                'days_until_stockout': days_until_stockout,
                'supplier': item.supplier
            })

        return create_response(
            data={
                'predictions': predictions_data,
                'count': len(predictions_data),
                'timeframe_days': days_ahead
            },
            message=f"Predicted {len(predictions_data)} potential stockouts in {days_ahead} days"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to predict stockouts")

# ==============================================================================
# REPORTING ENDPOINTS
# ==============================================================================

@inventory_api.route('/reports/export', methods=['POST'])
@cross_origin()
def export_inventory_report():
    """
    POST /api/inventory/reports/export
    Export comprehensive inventory report
    Body: {
        "format": "excel|json",
        "include_analytics": boolean,
        "filename": "string (optional)"
    }
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        data = request.get_json() or {}
        format_type = data.get('format', 'excel').lower()
        include_analytics = data.get('include_analytics', True)
        filename = data.get('filename')

        if format_type == 'excel':
            # Generate Excel report
            file_path = inventory_manager.export_inventory_report(filename)
            return create_response(
                data={'file_path': file_path},
                message="Excel report generated successfully"
            )
        elif format_type == 'json':
            # Generate JSON report
            report = {
                'summary': inventory_manager.get_inventory_summary(),
                'items': [
                    {
                        'item_code': item.item_code,
                        'item_name': item.item_name,
                        'category': item.category,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'total_value': item.total_value,
                        'supplier': item.supplier,
                        'stock_level': item.stock_level_category.value
                    }
                    for item in inventory_manager.items.values()
                ]
            }

            if include_analytics:
                report['analytics'] = inventory_manager.get_analytics()

            return create_response(
                data=report,
                message="JSON report generated successfully"
            )
        else:
            return create_response(
                message=f"Unsupported format: {format_type}",
                status=400,
                success=False
            )

    except Exception as e:
        return handle_api_error(e, "Failed to export report")

@inventory_api.route('/audit-trail', methods=['GET'])
@cross_origin()
def get_audit_trail():
    """
    GET /api/inventory/audit-trail?item_code=&days=
    Returns audit trail for inventory changes
    """
    try:
        if not inventory_manager:
            return create_response(message="Inventory service not initialized", status=503, success=False)

        item_code = request.args.get('item_code')
        days = int(request.args.get('days', 30))

        audit_trail = inventory_manager.get_audit_trail(item_code, days)

        return create_response(
            data={
                'audit_trail': audit_trail,
                'count': len(audit_trail),
                'filters': {
                    'item_code': item_code,
                    'days': days
                }
            },
            message=f"Retrieved {len(audit_trail)} audit trail entries"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to retrieve audit trail")

# ==============================================================================
# UTILITY ENDPOINTS
# ==============================================================================

@inventory_api.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """
    GET /api/inventory/health
    Health check endpoint
    """
    try:
        status = {
            'service': 'inventory_api',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'inventory_manager_initialized': inventory_manager is not None,
            'excel_processor_initialized': excel_processor is not None
        }

        if inventory_manager:
            status['total_items'] = len(inventory_manager.items)
            status['active_alerts'] = len([a for a in inventory_manager.alerts if not a.resolved])

        return create_response(
            data=status,
            message="Service is healthy"
        )

    except Exception as e:
        return handle_api_error(e, "Health check failed")

@inventory_api.route('/refresh', methods=['POST'])
@cross_origin()
def refresh_inventory_data():
    """
    POST /api/inventory/refresh
    Refresh inventory data from Excel files
    """
    try:
        if not inventory_manager or not excel_processor:
            return create_response(message="Services not initialized", status=503, success=False)

        # Clear cache and reload data
        excel_processor.clear_cache()
        inventory_manager._load_inventory_data()

        summary = inventory_manager.get_inventory_summary()

        return create_response(
            data={
                'total_items': summary['total_items'],
                'total_value': summary['total_value'],
                'alert_count': summary['alerts']['total']
            },
            message="Inventory data refreshed successfully"
        )

    except Exception as e:
        return handle_api_error(e, "Failed to refresh inventory data")