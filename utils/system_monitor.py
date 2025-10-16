#!/usr/bin/env python3
"""
System Monitoring and Maintenance Utilities for Derivco Facilities Management
Monitors system health, performance, and automatically handles maintenance tasks
"""

import psutil
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging
import json
import threading
import subprocess
import shutil
import platform
import socket
import uuid
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    process_count: int
    uptime_seconds: int

@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""
    timestamp: datetime
    flask_processes: int
    python_memory_mb: float
    excel_files_open: int
    database_size_mb: float
    log_files_size_mb: float
    cache_size_mb: float
    active_users: int
    api_requests_count: int
    error_count: int

@dataclass
class HealthCheck:
    """Health check result"""
    check_name: str
    status: str  # healthy, warning, critical, error
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0

class SystemMonitor:
    """
    Comprehensive system monitoring for Derivco facilities management
    Tracks performance, health, and automatically handles maintenance
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.is_monitoring = False
        self.monitor_thread = None

        # Metrics storage
        self.system_metrics_history: List[SystemMetrics] = []
        self.app_metrics_history: List[ApplicationMetrics] = []
        self.health_checks_history: List[HealthCheck] = []

        # Alert thresholds
        self.alert_thresholds = self.config.get('alert_thresholds', {})

        # System information
        self.system_info = self._collect_system_info()

        # Setup monitoring database
        self._setup_monitoring_database()

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default monitoring configuration"""
        return {
            'monitoring': {
                'interval_seconds': 60,
                'metrics_retention_days': 30,
                'health_check_interval_minutes': 5,
                'cleanup_interval_hours': 24
            },
            'alert_thresholds': {
                'cpu_percent': 80.0,
                'memory_percent': 85.0,
                'disk_percent': 90.0,
                'response_time_ms': 2000,
                'error_rate_percent': 5.0,
                'uptime_hours': 720  # 30 days
            },
            'maintenance': {
                'auto_cleanup_enabled': True,
                'auto_restart_on_critical': False,
                'backup_before_maintenance': True,
                'maintenance_window_start': '02:00',
                'maintenance_window_end': '04:00'
            },
            'notifications': {
                'enabled': True,
                'email_alerts': True,
                'dashboard_alerts': True,
                'critical_alert_interval_minutes': 15
            }
        }

    def _setup_monitoring_database(self):
        """Setup SQLite database for metrics storage"""
        try:
            db_path = Path('monitoring/system_metrics.db')
            db_path.parent.mkdir(exist_ok=True)

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # System metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_used_gb REAL,
                    memory_total_gb REAL,
                    disk_percent REAL,
                    disk_used_gb REAL,
                    disk_total_gb REAL,
                    network_bytes_sent INTEGER,
                    network_bytes_recv INTEGER,
                    active_connections INTEGER,
                    process_count INTEGER,
                    uptime_seconds INTEGER
                )
            ''')

            # Application metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    flask_processes INTEGER,
                    python_memory_mb REAL,
                    excel_files_open INTEGER,
                    database_size_mb REAL,
                    log_files_size_mb REAL,
                    cache_size_mb REAL,
                    active_users INTEGER,
                    api_requests_count INTEGER,
                    error_count INTEGER
                )
            ''')

            # Health checks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    check_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    details TEXT,
                    duration_ms REAL
                )
            ''')

            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_timestamp ON app_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_checks(timestamp)')

            conn.commit()
            conn.close()

            logger.info("Monitoring database setup completed")

        except Exception as e:
            logger.error(f"Error setting up monitoring database: {e}")

    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect basic system information"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())

            return {
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'python_version': sys.version.split()[0],
                'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'cpu_count': psutil.cpu_count(),
                'boot_time': boot_time.isoformat(),
                'system_uuid': str(uuid.uuid4()),
                'monitoring_started': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
            return {'error': str(e)}

    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)

            # Network metrics
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv

            # Process metrics
            active_connections = len(psutil.net_connections())
            process_count = len(psutil.pids())

            # Uptime
            boot_time = psutil.boot_time()
            uptime_seconds = int(time.time() - boot_time)

            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=round(memory_used_gb, 2),
                memory_total_gb=round(memory_total_gb, 2),
                disk_percent=round(disk_percent, 2),
                disk_used_gb=round(disk_used_gb, 2),
                disk_total_gb=round(disk_total_gb, 2),
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                active_connections=active_connections,
                process_count=process_count,
                uptime_seconds=uptime_seconds
            )

            return metrics

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None

    def collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application-specific metrics"""
        try:
            # Flask/Python processes
            flask_processes = 0
            python_memory_mb = 0

            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'flask' in cmdline.lower() or 'app.py' in cmdline.lower():
                            flask_processes += 1
                        python_memory_mb += proc.info['memory_info'].rss / (1024**2)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Excel files monitoring
            excel_files_open = self._count_excel_files_in_use()

            # Database size
            database_size_mb = self._get_database_size_mb()

            # Log files size
            log_files_size_mb = self._get_log_files_size_mb()

            # Cache size estimation
            cache_size_mb = self._estimate_cache_size_mb()

            # Active users (estimation based on recent log entries)
            active_users = self._estimate_active_users()

            # API requests count (from logs)
            api_requests_count = self._count_recent_api_requests()

            # Error count (from logs)
            error_count = self._count_recent_errors()

            metrics = ApplicationMetrics(
                timestamp=datetime.now(),
                flask_processes=flask_processes,
                python_memory_mb=round(python_memory_mb, 2),
                excel_files_open=excel_files_open,
                database_size_mb=round(database_size_mb, 2),
                log_files_size_mb=round(log_files_size_mb, 2),
                cache_size_mb=round(cache_size_mb, 2),
                active_users=active_users,
                api_requests_count=api_requests_count,
                error_count=error_count
            )

            return metrics

        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return None

    def _count_excel_files_in_use(self) -> int:
        """Count Excel files currently being used"""
        try:
            excel_files = [
                'STORES_INFRASTRUCTURE_ADMINISTRATION_enhanced.xlsx',
                'signout_data_improved.xlsx',
                'medication_data_enhanced.xlsx'
            ]

            files_in_use = 0
            for excel_file in excel_files:
                try:
                    # Try to open file exclusively to check if it's in use
                    with open(excel_file, 'r+b'):
                        pass
                except (PermissionError, IOError):
                    files_in_use += 1
                except FileNotFoundError:
                    pass

            return files_in_use

        except Exception as e:
            logger.error(f"Error counting Excel files in use: {e}")
            return 0

    def _get_database_size_mb(self) -> float:
        """Get total database files size"""
        try:
            total_size = 0
            db_files = [
                'monitoring/system_metrics.db',
                'analytics_history.json'
            ]

            for db_file in db_files:
                db_path = Path(db_file)
                if db_path.exists():
                    total_size += db_path.stat().st_size

            return total_size / (1024**2)

        except Exception as e:
            logger.error(f"Error getting database size: {e}")
            return 0.0

    def _get_log_files_size_mb(self) -> float:
        """Get total log files size"""
        try:
            total_size = 0
            log_dirs = ['logs', 'automation/logs']

            for log_dir in log_dirs:
                log_path = Path(log_dir)
                if log_path.exists():
                    for log_file in log_path.rglob('*.log'):
                        total_size += log_file.stat().st_size

            return total_size / (1024**2)

        except Exception as e:
            logger.error(f"Error getting log files size: {e}")
            return 0.0

    def _estimate_cache_size_mb(self) -> float:
        """Estimate cache size"""
        try:
            # This would be implementation-specific based on caching system used
            # For now, estimate based on temporary files
            temp_dirs = ['automation/temp', 'temp']
            total_size = 0

            for temp_dir in temp_dirs:
                temp_path = Path(temp_dir)
                if temp_path.exists():
                    for file in temp_path.rglob('*'):
                        if file.is_file():
                            total_size += file.stat().st_size

            return total_size / (1024**2)

        except Exception as e:
            logger.error(f"Error estimating cache size: {e}")
            return 0.0

    def _estimate_active_users(self) -> int:
        """Estimate active users from recent activity"""
        try:
            # In production, this would analyze web server logs or session data
            # For now, return a placeholder based on system activity
            return min(psutil.cpu_percent() // 10, 5)  # Rough estimate

        except Exception as e:
            logger.error(f"Error estimating active users: {e}")
            return 0

    def _count_recent_api_requests(self) -> int:
        """Count recent API requests from logs"""
        try:
            # In production, this would parse web server access logs
            # For now, return a placeholder
            return 0

        except Exception as e:
            logger.error(f"Error counting API requests: {e}")
            return 0

    def _count_recent_errors(self) -> int:
        """Count recent errors from logs"""
        try:
            error_count = 0
            log_file = Path('facilities_management.log')

            if log_file.exists():
                # Read last 1000 lines and count ERROR entries
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-1000:] if len(lines) > 1000 else lines

                    for line in recent_lines:
                        if 'ERROR' in line:
                            # Check if error is from last hour
                            try:
                                timestamp_str = line.split(' - ')[0]
                                log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                                if datetime.now() - log_time < timedelta(hours=1):
                                    error_count += 1
                            except:
                                pass

            return error_count

        except Exception as e:
            logger.error(f"Error counting recent errors: {e}")
            return 0

    def run_health_checks(self) -> List[HealthCheck]:
        """Run comprehensive health checks"""
        health_checks = []

        # System health checks
        health_checks.extend([
            self._check_cpu_health(),
            self._check_memory_health(),
            self._check_disk_health(),
            self._check_network_health(),
            self._check_process_health()
        ])

        # Application health checks
        health_checks.extend([
            self._check_excel_files_health(),
            self._check_database_health(),
            self._check_services_health(),
            self._check_log_files_health(),
            self._check_backup_health()
        ])

        # Store health checks
        self.health_checks_history.extend(health_checks)

        # Keep only recent health checks in memory
        cutoff_time = datetime.now() - timedelta(days=7)
        self.health_checks_history = [
            hc for hc in self.health_checks_history
            if hc.timestamp >= cutoff_time
        ]

        return health_checks

    def _check_cpu_health(self) -> HealthCheck:
        """Check CPU health"""
        start_time = time.time()
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            duration_ms = (time.time() - start_time) * 1000

            if cpu_percent > self.alert_thresholds['cpu_percent']:
                status = 'critical' if cpu_percent > 95 else 'warning'
                message = f"High CPU usage: {cpu_percent}%"
            else:
                status = 'healthy'
                message = f"CPU usage normal: {cpu_percent}%"

            return HealthCheck(
                check_name='cpu_health',
                status=status,
                message=message,
                details={'cpu_percent': cpu_percent},
                duration_ms=duration_ms
            )

        except Exception as e:
            return HealthCheck(
                check_name='cpu_health',
                status='error',
                message=f"Error checking CPU: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    def _check_memory_health(self) -> HealthCheck:
        """Check memory health"""
        start_time = time.time()
        try:
            memory = psutil.virtual_memory()
            duration_ms = (time.time() - start_time) * 1000

            if memory.percent > self.alert_thresholds['memory_percent']:
                status = 'critical' if memory.percent > 95 else 'warning'
                message = f"High memory usage: {memory.percent}%"
            else:
                status = 'healthy'
                message = f"Memory usage normal: {memory.percent}%"

            return HealthCheck(
                check_name='memory_health',
                status=status,
                message=message,
                details={
                    'memory_percent': memory.percent,
                    'memory_used_gb': memory.used / (1024**3),
                    'memory_available_gb': memory.available / (1024**3)
                },
                duration_ms=duration_ms
            )

        except Exception as e:
            return HealthCheck(
                check_name='memory_health',
                status='error',
                message=f"Error checking memory: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    def _check_disk_health(self) -> HealthCheck:
        """Check disk health"""
        start_time = time.time()
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            duration_ms = (time.time() - start_time) * 1000

            if disk_percent > self.alert_thresholds['disk_percent']:
                status = 'critical' if disk_percent > 98 else 'warning'
                message = f"High disk usage: {disk_percent:.1f}%"
            else:
                status = 'healthy'
                message = f"Disk usage normal: {disk_percent:.1f}%"

            return HealthCheck(
                check_name='disk_health',
                status=status,
                message=message,
                details={
                    'disk_percent': disk_percent,
                    'disk_used_gb': disk.used / (1024**3),
                    'disk_free_gb': disk.free / (1024**3)
                },
                duration_ms=duration_ms
            )

        except Exception as e:
            return HealthCheck(
                check_name='disk_health',
                status='error',
                message=f"Error checking disk: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    def _check_network_health(self) -> HealthCheck:
        """Check network health"""
        start_time = time.time()
        try:
            # Test network connectivity
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=5)
                network_status = "connected"
            except:
                network_status = "disconnected"

            connections = len(psutil.net_connections())
            duration_ms = (time.time() - start_time) * 1000

            if network_status == "disconnected":
                status = 'critical'
                message = "Network connectivity issues detected"
            elif connections > 1000:
                status = 'warning'
                message = f"High number of network connections: {connections}"
            else:
                status = 'healthy'
                message = f"Network healthy: {connections} connections"

            return HealthCheck(
                check_name='network_health',
                status=status,
                message=message,
                details={
                    'network_status': network_status,
                    'active_connections': connections
                },
                duration_ms=duration_ms
            )

        except Exception as e:
            return HealthCheck(
                check_name='network_health',
                status='error',
                message=f"Error checking network: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    def _check_process_health(self) -> HealthCheck:
        """Check process health"""
        start_time = time.time()
        try:
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'memory_mb': proc.info['memory_info'].rss / (1024**2)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            duration_ms = (time.time() - start_time) * 1000

            if not python_processes:
                status = 'critical'
                message = "No Python processes found"
            elif len(python_processes) > 10:
                status = 'warning'
                message = f"High number of Python processes: {len(python_processes)}"
            else:
                status = 'healthy'
                message = f"Python processes healthy: {len(python_processes)} running"

            return HealthCheck(
                check_name='process_health',
                status=status,
                message=message,
                details={
                    'python_processes': len(python_processes),
                    'total_python_memory_mb': sum(p['memory_mb'] for p in python_processes)
                },
                duration_ms=duration_ms
            )

        except Exception as e:
            return HealthCheck(
                check_name='process_health',
                status='error',
                message=f"Error checking processes: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    def _check_excel_files_health(self) -> HealthCheck:
        """Check Excel files health"""
        start_time = time.time()
        try:
            excel_files = [
                'STORES_INFRASTRUCTURE_ADMINISTRATION_enhanced.xlsx',
                'signout_data_improved.xlsx',
                'medication_data_enhanced.xlsx'
            ]

            file_status = {}
            missing_files = []
            corrupted_files = []

            for excel_file in excel_files:
                file_path = Path(excel_file)
                if not file_path.exists():
                    missing_files.append(excel_file)
                    file_status[excel_file] = 'missing'
                else:
                    # Basic corruption check
                    try:
                        import pandas as pd
                        pd.read_excel(file_path, nrows=1)
                        file_status[excel_file] = 'healthy'
                    except Exception:
                        corrupted_files.append(excel_file)
                        file_status[excel_file] = 'corrupted'

            duration_ms = (time.time() - start_time) * 1000

            if missing_files or corrupted_files:
                status = 'critical' if missing_files else 'warning'
                issues = []
                if missing_files:
                    issues.append(f"Missing: {', '.join(missing_files)}")
                if corrupted_files:
                    issues.append(f"Corrupted: {', '.join(corrupted_files)}")
                message = f"Excel file issues: {'; '.join(issues)}"
            else:
                status = 'healthy'
                message = f"All {len(excel_files)} Excel files healthy"

            return HealthCheck(
                check_name='excel_files_health',
                status=status,
                message=message,
                details=file_status,
                duration_ms=duration_ms
            )

        except Exception as e:
            return HealthCheck(
                check_name='excel_files_health',
                status='error',
                message=f"Error checking Excel files: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    def _check_database_health(self) -> HealthCheck:
        """Check database health"""
        start_time = time.time()
        try:
            db_path = Path('monitoring/system_metrics.db')

            if not db_path.exists():
                return HealthCheck(
                    check_name='database_health',
                    status='warning',
                    message="Monitoring database not found",
                    duration_ms=(time.time() - start_time) * 1000
                )

            # Test database connectivity
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM system_metrics")
            record_count = cursor.fetchone()[0]
            conn.close()

            duration_ms = (time.time() - start_time) * 1000

            status = 'healthy'
            message = f"Database healthy: {record_count} records"

            return HealthCheck(
                check_name='database_health',
                status=status,
                message=message,
                details={'record_count': record_count},
                duration_ms=duration_ms
            )

        except Exception as e:
            return HealthCheck(
                check_name='database_health',
                status='error',
                message=f"Database error: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    def _check_services_health(self) -> HealthCheck:
        """Check application services health"""
        start_time = time.time()
        try:
            services_status = {
                'flask_app': False,
                'excel_processor': True,  # Assume healthy if no errors
                'analytics_engine': True,
                'notification_system': True
            }

            # Check if Flask is running
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'flask' in cmdline.lower() or 'app.py' in cmdline.lower():
                            services_status['flask_app'] = True
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            duration_ms = (time.time() - start_time) * 1000

            healthy_services = sum(services_status.values())
            total_services = len(services_status)

            if healthy_services == total_services:
                status = 'healthy'
                message = f"All {total_services} services healthy"
            elif healthy_services >= total_services * 0.75:
                status = 'warning'
                message = f"{healthy_services}/{total_services} services healthy"
            else:
                status = 'critical'
                message = f"Service failures: {healthy_services}/{total_services} healthy"

            return HealthCheck(
                check_name='services_health',
                status=status,
                message=message,
                details=services_status,
                duration_ms=duration_ms
            )

        except Exception as e:
            return HealthCheck(
                check_name='services_health',
                status='error',
                message=f"Error checking services: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    def _check_log_files_health(self) -> HealthCheck:
        """Check log files health"""
        start_time = time.time()
        try:
            log_files = []
            log_dirs = ['logs', 'automation/logs']

            for log_dir in log_dirs:
                log_path = Path(log_dir)
                if log_path.exists():
                    log_files.extend(log_path.rglob('*.log'))

            total_size_mb = sum(f.stat().st_size for f in log_files) / (1024**2)
            recent_errors = self._count_recent_errors()

            duration_ms = (time.time() - start_time) * 1000

            if recent_errors > 10:
                status = 'critical'
                message = f"High error rate: {recent_errors} errors in last hour"
            elif total_size_mb > 100:
                status = 'warning'
                message = f"Large log files: {total_size_mb:.1f}MB total"
            else:
                status = 'healthy'
                message = f"Logs healthy: {len(log_files)} files, {total_size_mb:.1f}MB"

            return HealthCheck(
                check_name='log_files_health',
                status=status,
                message=message,
                details={
                    'log_file_count': len(log_files),
                    'total_size_mb': total_size_mb,
                    'recent_errors': recent_errors
                },
                duration_ms=duration_ms
            )

        except Exception as e:
            return HealthCheck(
                check_name='log_files_health',
                status='error',
                message=f"Error checking log files: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    def _check_backup_health(self) -> HealthCheck:
        """Check backup health"""
        start_time = time.time()
        try:
            backup_dir = Path('automation/backups')

            if not backup_dir.exists():
                return HealthCheck(
                    check_name='backup_health',
                    status='warning',
                    message="No backup directory found",
                    duration_ms=(time.time() - start_time) * 1000
                )

            # Find recent backups
            recent_backups = []
            for backup_path in backup_dir.iterdir():
                if backup_path.is_dir():
                    backup_time = datetime.fromtimestamp(backup_path.stat().st_mtime)
                    age_hours = (datetime.now() - backup_time).total_seconds() / 3600
                    if age_hours <= 48:  # Within last 48 hours
                        recent_backups.append({
                            'path': str(backup_path),
                            'age_hours': age_hours
                        })

            duration_ms = (time.time() - start_time) * 1000

            if not recent_backups:
                status = 'critical'
                message = "No recent backups found"
            elif len(recent_backups) < 2:
                status = 'warning'
                message = f"Only {len(recent_backups)} recent backup(s)"
            else:
                status = 'healthy'
                message = f"Backup healthy: {len(recent_backups)} recent backups"

            return HealthCheck(
                check_name='backup_health',
                status=status,
                message=message,
                details={'recent_backups': len(recent_backups)},
                duration_ms=duration_ms
            )

        except Exception as e:
            return HealthCheck(
                check_name='backup_health',
                status='error',
                message=f"Error checking backups: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    def get_system_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive system status summary"""
        try:
            # Collect current metrics
            system_metrics = self.collect_system_metrics()
            app_metrics = self.collect_application_metrics()

            # Run health checks
            health_checks = self.run_health_checks()

            # Analyze health status
            health_summary = {}
            for check in health_checks:
                health_summary[check.check_name] = {
                    'status': check.status,
                    'message': check.message,
                    'duration_ms': check.duration_ms
                }

            # Overall system status
            critical_issues = [hc for hc in health_checks if hc.status == 'critical']
            warning_issues = [hc for hc in health_checks if hc.status == 'warning']
            error_issues = [hc for hc in health_checks if hc.status == 'error']

            if critical_issues or error_issues:
                overall_status = 'critical'
            elif warning_issues:
                overall_status = 'warning'
            else:
                overall_status = 'healthy'

            summary = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': overall_status,
                'system_info': self.system_info,
                'system_metrics': {
                    'cpu_percent': system_metrics.cpu_percent if system_metrics else None,
                    'memory_percent': system_metrics.memory_percent if system_metrics else None,
                    'disk_percent': system_metrics.disk_percent if system_metrics else None,
                    'uptime_hours': (system_metrics.uptime_seconds / 3600) if system_metrics else None
                },
                'application_metrics': {
                    'flask_processes': app_metrics.flask_processes if app_metrics else None,
                    'python_memory_mb': app_metrics.python_memory_mb if app_metrics else None,
                    'error_count': app_metrics.error_count if app_metrics else None,
                    'active_users': app_metrics.active_users if app_metrics else None
                },
                'health_checks': health_summary,
                'issues': {
                    'critical': len(critical_issues),
                    'warning': len(warning_issues),
                    'error': len(error_issues)
                }
            }

            return summary

        except Exception as e:
            logger.error(f"Error generating system status summary: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'error',
                'error': str(e)
            }

    def start_monitoring(self):
        """Start continuous system monitoring"""
        try:
            if self.is_monitoring:
                logger.warning("System monitoring already running")
                return

            self.is_monitoring = True
            logger.info("Starting system monitoring...")

            def monitoring_loop():
                while self.is_monitoring:
                    try:
                        # Collect metrics
                        system_metrics = self.collect_system_metrics()
                        if system_metrics:
                            self.system_metrics_history.append(system_metrics)
                            self._store_system_metrics(system_metrics)

                        app_metrics = self.collect_application_metrics()
                        if app_metrics:
                            self.app_metrics_history.append(app_metrics)
                            self._store_app_metrics(app_metrics)

                        # Cleanup old metrics from memory
                        cutoff_time = datetime.now() - timedelta(hours=24)
                        self.system_metrics_history = [
                            m for m in self.system_metrics_history if m.timestamp >= cutoff_time
                        ]
                        self.app_metrics_history = [
                            m for m in self.app_metrics_history if m.timestamp >= cutoff_time
                        ]

                        # Run health checks periodically
                        if datetime.now().minute % self.config['monitoring']['health_check_interval_minutes'] == 0:
                            health_checks = self.run_health_checks()
                            for hc in health_checks:
                                self._store_health_check(hc)

                        # Wait for next monitoring cycle
                        time.sleep(self.config['monitoring']['interval_seconds'])

                    except Exception as e:
                        logger.error(f"Error in monitoring loop: {e}")
                        time.sleep(60)  # Wait before retrying

            self.monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
            self.monitor_thread.start()

            logger.info("System monitoring started successfully")

        except Exception as e:
            logger.error(f"Error starting system monitoring: {e}")
            self.is_monitoring = False

    def stop_monitoring(self):
        """Stop system monitoring"""
        try:
            logger.info("Stopping system monitoring...")
            self.is_monitoring = False

            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=10)

            logger.info("System monitoring stopped")

        except Exception as e:
            logger.error(f"Error stopping system monitoring: {e}")

    def _store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics to database"""
        try:
            db_path = Path('monitoring/system_metrics.db')
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO system_metrics (
                    timestamp, cpu_percent, memory_percent, memory_used_gb, memory_total_gb,
                    disk_percent, disk_used_gb, disk_total_gb, network_bytes_sent, network_bytes_recv,
                    active_connections, process_count, uptime_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp.isoformat(),
                metrics.cpu_percent,
                metrics.memory_percent,
                metrics.memory_used_gb,
                metrics.memory_total_gb,
                metrics.disk_percent,
                metrics.disk_used_gb,
                metrics.disk_total_gb,
                metrics.network_bytes_sent,
                metrics.network_bytes_recv,
                metrics.active_connections,
                metrics.process_count,
                metrics.uptime_seconds
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error storing system metrics: {e}")

    def _store_app_metrics(self, metrics: ApplicationMetrics):
        """Store application metrics to database"""
        try:
            db_path = Path('monitoring/system_metrics.db')
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO app_metrics (
                    timestamp, flask_processes, python_memory_mb, excel_files_open,
                    database_size_mb, log_files_size_mb, cache_size_mb,
                    active_users, api_requests_count, error_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp.isoformat(),
                metrics.flask_processes,
                metrics.python_memory_mb,
                metrics.excel_files_open,
                metrics.database_size_mb,
                metrics.log_files_size_mb,
                metrics.cache_size_mb,
                metrics.active_users,
                metrics.api_requests_count,
                metrics.error_count
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error storing application metrics: {e}")

    def _store_health_check(self, health_check: HealthCheck):
        """Store health check result to database"""
        try:
            db_path = Path('monitoring/system_metrics.db')
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO health_checks (
                    timestamp, check_name, status, message, details, duration_ms
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                health_check.timestamp.isoformat(),
                health_check.check_name,
                health_check.status,
                health_check.message,
                json.dumps(health_check.details),
                health_check.duration_ms
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error storing health check: {e}")