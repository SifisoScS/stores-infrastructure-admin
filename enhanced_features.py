#!/usr/bin/env python3
"""
Enhanced Features for Existing Derivco Inventory System
Practical improvements using current Flask/Python/Excel stack
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from collections import Counter, defaultdict

# Email imports - may not be needed for basic functionality
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# Note: sklearn not installed, using basic analytics instead
SKLEARN_AVAILABLE = False
try:
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("sklearn not available - using basic analytics fallback")

class InventoryIntelligence:
    """AI-powered inventory insights using existing data"""

    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.history_file = "inventory_usage_history.json"
        self.predictions_cache = "predictions_cache.json"
        self.load_usage_history()

    def load_usage_history(self):
        """Load historical usage data"""
        try:
            with open(self.history_file, 'r') as f:
                self.usage_history = json.load(f)
        except FileNotFoundError:
            self.usage_history = {}
            self.save_usage_history()

    def save_usage_history(self):
        """Save usage history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.usage_history, f, indent=2, default=str)

    def record_item_usage(self, item_id, quantity_used, date=None):
        """Record item usage for predictive analytics"""
        if date is None:
            date = datetime.now().isoformat()

        if item_id not in self.usage_history:
            self.usage_history[item_id] = []

        self.usage_history[item_id].append({
            'date': date,
            'quantity_used': quantity_used,
            'timestamp': datetime.now().isoformat()
        })

        self.save_usage_history()

    def predict_stock_depletion(self, item_id, current_stock):
        """Predict when an item will run out of stock"""
        if item_id not in self.usage_history or len(self.usage_history[item_id]) < 3:
            # Generate a basic prediction for demo purposes if no history
            if current_stock <= 5:
                days_until_empty = max(1, current_stock / 0.5)  # Assume 0.5 daily usage
                return {
                    'days_until_empty': round(days_until_empty, 1),
                    'predicted_depletion_date': (datetime.now() + timedelta(days=days_until_empty)).strftime('%Y-%m-%d'),
                    'average_daily_usage': 0.5,
                    'urgency_level': self.calculate_urgency(days_until_empty)
                }
            return None

        usage_data = self.usage_history[item_id]
        recent_usage = usage_data[-10:]  # Last 10 usage records

        # Calculate daily usage rate
        daily_usage = sum(u['quantity_used'] for u in recent_usage) / len(recent_usage)

        if daily_usage <= 0:
            daily_usage = 0.1  # Minimum usage rate to avoid division by zero

        days_until_empty = max(0.1, current_stock / daily_usage)
        depletion_date = datetime.now() + timedelta(days=days_until_empty)

        return {
            'days_until_empty': round(days_until_empty, 1),
            'predicted_depletion_date': depletion_date.strftime('%Y-%m-%d'),
            'average_daily_usage': round(daily_usage, 2),
            'urgency_level': self.calculate_urgency(days_until_empty)
        }

    def calculate_urgency(self, days_until_empty):
        """Calculate urgency level based on days until stock depletion"""
        if days_until_empty <= 3:
            return "CRITICAL"
        elif days_until_empty <= 7:
            return "HIGH"
        elif days_until_empty <= 14:
            return "MEDIUM"
        else:
            return "LOW"

    def get_smart_reorder_recommendations(self):
        """Get AI-powered reorder recommendations"""
        recommendations = []
        all_items = self.data_loader.get_all_items()

        for item in all_items:
            current_stock = item.get('current_stock', 0)
            prediction = self.predict_stock_depletion(item['id'], current_stock)

            if prediction and prediction['urgency_level'] in ['CRITICAL', 'HIGH']:
                # Calculate optimal order quantity
                avg_daily_usage = prediction['average_daily_usage']
                safety_stock_days = 30  # 30 days safety stock
                optimal_quantity = int(avg_daily_usage * safety_stock_days)

                recommendations.append({
                    'item': item,
                    'prediction': prediction,
                    'recommended_order_quantity': optimal_quantity,
                    'cost_estimate': optimal_quantity * item.get('unit_cost', 0),
                    'supplier': item.get('supplier', 'TBD')
                })

        return sorted(recommendations, key=lambda x: x['prediction']['urgency_level'])

class SmartAlertSystem:
    """Intelligent alerting system using existing infrastructure"""

    def __init__(self, data_loader, inventory_intelligence):
        self.data_loader = data_loader
        self.intelligence = inventory_intelligence
        self.alerts_file = "active_alerts.json"
        self.notification_settings = self.load_notification_settings()

    def load_notification_settings(self):
        """Load notification settings"""
        try:
            with open("notification_settings.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            default_settings = {
                "email_alerts": True,
                "critical_threshold_days": 3,
                "high_threshold_days": 7,
                "recipients": ["facilities@derivco.com", "sifiso.shezi@derivco.com"],
                "alert_frequency": "daily"
            }
            self.save_notification_settings(default_settings)
            return default_settings

    def save_notification_settings(self, settings):
        """Save notification settings"""
        with open("notification_settings.json", 'w') as f:
            json.dump(settings, f, indent=2)

    def generate_daily_intelligence_report(self):
        """Generate daily intelligence report"""
        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'summary': {},
            'critical_alerts': [],
            'predictive_insights': [],
            'cost_savings_opportunities': [],
            'compliance_reminders': []
        }

        # Get smart recommendations
        recommendations = self.intelligence.get_smart_reorder_recommendations()
        critical_items = [r for r in recommendations if r['prediction']['urgency_level'] == 'CRITICAL']
        high_priority = [r for r in recommendations if r['prediction']['urgency_level'] == 'HIGH']

        # Summary statistics
        report['summary'] = {
            'total_items_monitored': len(self.data_loader.get_all_items()),
            'critical_stock_items': len(critical_items),
            'high_priority_items': len(high_priority),
            'total_estimated_reorder_cost': sum(r['cost_estimate'] for r in recommendations)
        }

        # Critical alerts
        for item_rec in critical_items:
            report['critical_alerts'].append({
                'item_name': item_rec['item']['name'],
                'current_stock': item_rec['item']['current_stock'],
                'days_until_empty': item_rec['prediction']['days_until_empty'],
                'recommended_action': f"Order {item_rec['recommended_order_quantity']} units immediately"
            })

        # Predictive insights
        for item_rec in recommendations[:5]:  # Top 5 insights
            report['predictive_insights'].append({
                'item_name': item_rec['item']['name'],
                'prediction': f"Will run out in {item_rec['prediction']['days_until_empty']} days",
                'usage_pattern': f"Average daily usage: {item_rec['prediction']['average_daily_usage']} units",
                'recommendation': f"Order {item_rec['recommended_order_quantity']} units"
            })

        return report

    def send_email_alert(self, subject, body, recipients=None):
        """Send email alerts (placeholder - configure with actual SMTP)"""
        if recipients is None:
            recipients = self.notification_settings['recipients']

        # For now, save email content to file for review (email libraries not available)
        email_content = {
            'timestamp': datetime.now().isoformat(),
            'subject': subject,
            'body': body,
            'recipients': recipients,
            'email_available': EMAIL_AVAILABLE
        }

        try:
            with open(f"email_alerts_{datetime.now().strftime('%Y%m%d')}.json", 'a') as f:
                f.write(json.dumps(email_content, indent=2) + "\n")
        except Exception as e:
            print(f"Could not save email alert: {e}")

class AdvancedAnalytics:
    """Advanced analytics using existing data"""

    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.analytics_cache = "analytics_cache.json"

    def calculate_inventory_health_score(self):
        """Calculate overall inventory health score"""
        all_items = self.data_loader.get_all_items()
        if not all_items:
            return 0

        scores = []
        for item in all_items:
            current_stock = item.get('current_stock', 0)
            min_stock = item.get('min_stock', 10)
            max_stock = item.get('max_stock', 100)

            if current_stock <= min_stock:
                score = 0  # Critical
            elif current_stock <= min_stock * 1.5:
                score = 25  # Poor
            elif current_stock <= max_stock * 0.8:
                score = 75  # Good
            else:
                score = 100  # Excellent

            scores.append(score)

        return round(sum(scores) / len(scores), 1)

    def get_category_performance_metrics(self):
        """Get performance metrics by category"""
        categories = self.data_loader.get_all_categories()
        metrics = {}

        for category_name in categories:
            category_items = self.data_loader.get_category_data(category_name)
            if not category_items:
                continue

            total_items = len(category_items)
            low_stock_items = len([item for item in category_items
                                 if item.get('current_stock', 0) <= item.get('min_stock', 10)])

            metrics[category_name] = {
                'total_items': total_items,
                'low_stock_items': low_stock_items,
                'stock_health_percentage': round(((total_items - low_stock_items) / total_items) * 100, 1),
                'category_icon': self.get_category_icon(category_name)
            }

        return metrics

    def get_category_icon(self, category_name):
        """Get Font Awesome icon for category"""
        icons = {
            'Electric': 'bolt',
            'Plumbing': 'tint',
            'Carpentry': 'hammer',
            'Painting': 'paint-brush',
            'Aircon': 'snowflake',
            'Ceiling Tiles': 'th',
            'Decoration': 'palette',
            'Parking & Signage': 'parking',
            'Safety': 'shield-alt',
            'Access Control': 'key'
        }
        return icons.get(category_name, 'box')

    def get_cost_optimization_opportunities(self):
        """Identify cost optimization opportunities"""
        opportunities = []
        all_items = self.data_loader.get_all_items()

        # Find overstock items
        for item in all_items:
            current_stock = item.get('current_stock', 0)
            max_stock = item.get('max_stock', 100)
            unit_cost = item.get('unit_cost', 0)

            if current_stock > max_stock * 1.2:  # 20% over max stock
                excess_value = (current_stock - max_stock) * unit_cost
                opportunities.append({
                    'type': 'OVERSTOCK',
                    'item_name': item.get('name', 'Unknown'),
                    'excess_quantity': current_stock - max_stock,
                    'excess_value': excess_value,
                    'recommendation': 'Consider redistributing to other locations or reducing next order'
                })

        return sorted(opportunities, key=lambda x: x['excess_value'], reverse=True)

class SmartDashboardData:
    """Enhanced dashboard data with intelligence"""

    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.intelligence = InventoryIntelligence(data_loader)
        self.analytics = AdvancedAnalytics(data_loader)
        self.alerts = SmartAlertSystem(data_loader, self.intelligence)

    def get_enhanced_dashboard_data(self):
        """Get enhanced dashboard data with AI insights"""
        base_data = self.data_loader.get_dashboard_data()

        # Add intelligent insights
        enhanced_data = {
            **base_data,
            'inventory_health_score': self.analytics.calculate_inventory_health_score(),
            'category_performance': self.analytics.get_category_performance_metrics(),
            'smart_recommendations': self.intelligence.get_smart_reorder_recommendations()[:5],
            'cost_optimization': self.analytics.get_cost_optimization_opportunities()[:3],
            'daily_intelligence_report': self.alerts.generate_daily_intelligence_report(),
            'system_insights': self.get_system_insights()
        }

        return enhanced_data

    def get_system_insights(self):
        """Get high-level system insights"""
        all_items = self.data_loader.get_all_items()
        if not all_items:
            return {}

        total_value = sum(item.get('current_stock', 0) * item.get('unit_cost', 0) for item in all_items)
        low_stock_value = sum(
            item.get('current_stock', 0) * item.get('unit_cost', 0)
            for item in all_items
            if item.get('current_stock', 0) <= item.get('min_stock', 10)
        )

        return {
            'total_inventory_value': round(total_value, 2),
            'at_risk_inventory_value': round(low_stock_value, 2),
            'risk_percentage': round((low_stock_value / total_value) * 100, 1) if total_value > 0 else 0,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'system_status': 'OPERATIONAL',
            'data_quality_score': self.calculate_data_quality_score()
        }

    def calculate_data_quality_score(self):
        """Calculate data quality score based on completeness"""
        all_items = self.data_loader.get_all_items()
        if not all_items:
            return 0

        required_fields = ['name', 'current_stock', 'min_stock', 'unit_cost']
        total_fields = len(all_items) * len(required_fields)
        complete_fields = 0

        for item in all_items:
            for field in required_fields:
                if item.get(field) is not None and item.get(field) != '':
                    complete_fields += 1

        return round((complete_fields / total_fields) * 100, 1) if total_fields > 0 else 0

# Export classes for use in main application
__all__ = ['InventoryIntelligence', 'SmartAlertSystem', 'AdvancedAnalytics', 'SmartDashboardData']