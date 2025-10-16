#!/usr/bin/env python3
"""
Seed Enhanced Data for AI Features
Creates sample usage history and analytics data for the enhanced features to work with
"""

import json
import os
from datetime import datetime, timedelta
import random

def create_sample_usage_history():
    """Create sample usage history for predictive analytics"""

    # Sample items with IDs
    sample_items = [
        {"id": "ELC001", "name": "LED Light Bulbs", "category": "Electric"},
        {"id": "PLM002", "name": "PVC Pipes", "category": "Plumbing"},
        {"id": "CAR003", "name": "Wood Screws", "category": "Carpentry"},
        {"id": "PAI004", "name": "White Paint", "category": "Painting"},
        {"id": "AIR005", "name": "AC Filters", "category": "Aircon"},
        {"id": "SAF006", "name": "Safety Gloves", "category": "Safety"},
        {"id": "ELC007", "name": "Electrical Wire", "category": "Electric"},
        {"id": "PLM008", "name": "Pipe Fittings", "category": "Plumbing"}
    ]

    usage_history = {}

    # Create 30 days of usage history for each item
    for item in sample_items:
        item_id = item["id"]
        usage_history[item_id] = []

        # Generate usage data for past 30 days
        for days_ago in range(30, 0, -1):
            usage_date = datetime.now() - timedelta(days=days_ago)

            # Simulate different usage patterns
            if item["category"] == "Electric":
                # Higher usage pattern
                quantity_used = random.randint(2, 8)
            elif item["category"] == "Safety":
                # Steady usage pattern
                quantity_used = random.randint(1, 3)
            else:
                # Variable usage pattern
                quantity_used = random.randint(0, 5)

            if quantity_used > 0:  # Only add if something was used
                usage_history[item_id].append({
                    'date': usage_date.isoformat(),
                    'quantity_used': quantity_used,
                    'timestamp': usage_date.isoformat()
                })

    return usage_history

def create_sample_predictions_cache():
    """Create sample predictions cache"""

    predictions = {
        "last_updated": datetime.now().isoformat(),
        "predictions": {
            "ELC001": {
                "days_until_empty": 7.2,
                "predicted_depletion_date": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                "average_daily_usage": 3.5,
                "urgency_level": "HIGH",
                "confidence": 0.85
            },
            "SAF006": {
                "days_until_empty": 2.1,
                "predicted_depletion_date": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                "average_daily_usage": 2.0,
                "urgency_level": "CRITICAL",
                "confidence": 0.92
            },
            "PLM002": {
                "days_until_empty": 15.8,
                "predicted_depletion_date": (datetime.now() + timedelta(days=16)).strftime('%Y-%m-%d'),
                "average_daily_usage": 1.2,
                "urgency_level": "MEDIUM",
                "confidence": 0.78
            }
        }
    }

    return predictions

def create_notification_settings():
    """Create notification settings"""

    settings = {
        "email_alerts": True,
        "critical_threshold_days": 3,
        "high_threshold_days": 7,
        "recipients": ["facilities@derivco.com", "sifiso.shezi@derivco.com"],
        "alert_frequency": "daily",
        "last_updated": datetime.now().isoformat()
    }

    return settings

def main():
    """Main function to seed enhanced data"""

    print("Seeding Enhanced Data for AI Features...")

    # Create usage history
    usage_history = create_sample_usage_history()
    with open("inventory_usage_history.json", 'w') as f:
        json.dump(usage_history, f, indent=2, default=str)
    print("Created inventory_usage_history.json")

    # Create predictions cache
    predictions_cache = create_sample_predictions_cache()
    with open("predictions_cache.json", 'w') as f:
        json.dump(predictions_cache, f, indent=2, default=str)
    print("Created predictions_cache.json")

    # Create notification settings
    notification_settings = create_notification_settings()
    with open("notification_settings.json", 'w') as f:
        json.dump(notification_settings, f, indent=2)
    print("Created notification_settings.json")

    # Create analytics cache
    analytics_cache = {
        "last_updated": datetime.now().isoformat(),
        "inventory_health_score": 87.3,
        "category_performance": {
            "Electric": {"health_percentage": 85.2, "total_items": 15},
            "Plumbing": {"health_percentage": 92.1, "total_items": 12},
            "Carpentry": {"health_percentage": 78.5, "total_items": 18},
            "Safety": {"health_percentage": 94.3, "total_items": 8}
        }
    }

    with open("analytics_cache.json", 'w') as f:
        json.dump(analytics_cache, f, indent=2, default=str)
    print("Created analytics_cache.json")

    print("\nEnhanced data seeding complete!")
    print("AI features now have sample data to work with")
    print("Start the application to see the enhanced features in action")

if __name__ == "__main__":
    main()