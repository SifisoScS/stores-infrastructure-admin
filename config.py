#!/usr/bin/env python3
"""
Configuration management for Enhanced Derivco Facilities Management System
Supports development, testing, and production environments
"""

import os
from pathlib import Path
from datetime import timedelta
from typing import Dict, Any

# Base directory
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base configuration class"""

    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'derivco-facilities-enhanced-secret-2024'
    FLASK_APP = 'enhanced_app.py'

    # Application settings
    APP_NAME = 'Derivco Facilities Management System'
    APP_VERSION = '2.0.0-enhanced'

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'pdf'}

    # Excel file paths
    EXCEL_FILES = {
        'inventory': 'STORES_INFRASTRUCTURE_ADMINISTRATION_enhanced.xlsx',
        'signout': 'signout_data_improved.xlsx',
        'medical': 'medication_data_enhanced.xlsx',
        'original_inventory': 'STORES_INFRASTRUCTURE_ADMINISTRATION.xlsx',
        'original_signout': 'signout_data.xlsx'
    }

    # Report generation settings
    REPORTS_FOLDER = BASE_DIR / 'reports'
    BACKUP_FOLDER = BASE_DIR / 'backups'
    LOGS_FOLDER = BASE_DIR / 'logs'

    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

    # Analytics settings
    ANALYTICS_HISTORY_FILE = 'analytics_history.json'
    MAX_HISTORICAL_RECORDS = 1000
    COMPLIANCE_THRESHOLD_EXCELLENT = 95.0
    COMPLIANCE_THRESHOLD_GOOD = 80.0
    COMPLIANCE_THRESHOLD_FAIR = 60.0

    # Inventory settings
    DEFAULT_REORDER_LEVEL = 10
    DEFAULT_MAX_STOCK_LEVEL = 100
    LOW_STOCK_THRESHOLD = 15
    CRITICAL_STOCK_THRESHOLD = 5

    # Notification settings
    EMAIL_ALERTS_ENABLED = False  # Set to True when email is configured
    SMS_ALERTS_ENABLED = False

    # API settings
    API_RATE_LIMIT = "100/hour"
    API_PAGINATION_DEFAULT = 50
    API_PAGINATION_MAX = 500

    # Security settings
    SESSION_TIMEOUT = timedelta(hours=8)
    PASSWORD_RESET_TIMEOUT = timedelta(hours=1)

    # Database settings (for future use)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        # Create necessary directories
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
        Config.REPORTS_FOLDER.mkdir(exist_ok=True)
        Config.BACKUP_FOLDER.mkdir(exist_ok=True)
        Config.LOGS_FOLDER.mkdir(exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False

    # Development-specific settings
    FLASK_ENV = 'development'

    # Enhanced logging in development
    LOG_LEVEL = 'DEBUG'

    # Cache disabled for development
    CACHE_TYPE = 'null'

    # Development database (SQLite for simplicity)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR / "facilities_dev.db"}'

    # Development API settings
    API_RATE_LIMIT = "1000/hour"  # More lenient for development

class TestingConfig(Config):
    """Testing configuration"""

    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False

    # Testing-specific settings
    FLASK_ENV = 'testing'

    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Test data files
    EXCEL_FILES = {
        'inventory': 'test_inventory.xlsx',
        'signout': 'test_signout.xlsx',
        'medical': 'test_medical.xlsx'
    }

    # Disable external services in testing
    EMAIL_ALERTS_ENABLED = False
    SMS_ALERTS_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False

    # Production-specific settings
    FLASK_ENV = 'production'

    # Production logging
    LOG_LEVEL = 'INFO'

    # Production database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                             f'sqlite:///{BASE_DIR / "facilities_prod.db"}'

    # Production cache (Redis recommended)
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')

    # Production security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Production API rate limiting
    API_RATE_LIMIT = "100/hour"

    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
                   ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # SMS configuration
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

    @staticmethod
    def init_app(app):
        """Initialize production app"""
        Config.init_app(app)

        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler

        # Set up file logging
        if not app.debug:
            file_handler = RotatingFileHandler(
                Config.LOGS_FOLDER / 'facilities_management.log',
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
            ))
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Derivco Facilities Management startup')

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config() -> Config:
    """Get the current configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

# Business logic configuration
BUSINESS_CONFIG = {
    # Compliance thresholds
    'compliance': {
        'work_order': {
            'excellent': 95.0,
            'good': 80.0,
            'fair': 60.0,
            'poor': 40.0
        },
        'tool_return': {
            'excellent': 98.0,
            'good': 90.0,
            'fair': 80.0,
            'poor': 70.0
        }
    },

    # Risk assessment levels
    'risk_levels': {
        'low': {'max_violations': 1, 'compliance_min': 90.0},
        'medium': {'max_violations': 3, 'compliance_min': 70.0},
        'high': {'max_violations': 5, 'compliance_min': 50.0},
        'critical': {'max_violations': float('inf'), 'compliance_min': 0.0}
    },

    # KPI targets
    'kpi_targets': {
        'transaction_volume_monthly': 120,
        'response_time_hours': 8,
        'equipment_utilization_percent': 70,
        'stock_availability_percent': 95,
        'inventory_turnover_annual': 6.0,
        'staff_productivity_transactions': 15
    },

    # Financial estimates
    'financial': {
        'average_tool_value': 500.0,
        'average_transaction_value': 500.0,
        'monthly_transactions_estimate': 100,
        'hourly_rate': 80.0
    },

    # Derivco-specific settings
    'derivco': {
        'departments': [
            'IT Department',
            'Facilities',
            'Security',
            'HR',
            'Finance',
            'Operations',
            'Maintenance',
            'Cleaning'
        ],
        'locations': [
            'Ground Floor',
            'First Floor',
            'Second Floor',
            'Third Floor',
            'Basement',
            'Roof',
            'Parking'
        ],
        'supervisor_names': {
            'Erasmus Ngwane',
            'Brindley Harrington',
            'Not Provided',
            'Not provided',
            'not provided',
            'N/A',
            'n/a',
            'None',
            'none',
            ''
        }
    }
}

# System capabilities configuration
SYSTEM_CAPABILITIES = {
    'excel_processing': True,
    'advanced_analytics': True,
    'real_time_compliance': True,
    'predictive_analytics': True,
    'automated_reporting': True,
    'api_access': True,
    'mobile_responsive': True,
    'audit_trail': True,
    'role_based_access': False,  # Future feature
    'email_notifications': False,  # Requires configuration
    'sms_alerts': False,  # Requires configuration
    'ai_insights': False,  # Future feature
    'iot_integration': False,  # Future feature
}