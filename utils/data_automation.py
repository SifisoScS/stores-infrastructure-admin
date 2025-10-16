#!/usr/bin/env python3
"""
Data Automation Utilities for Derivco Facilities Management
Automated data processing, validation, synchronization, and maintenance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import shutil
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
import json
import schedule
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# Import core services
import sys
sys.path.append('core')
sys.path.append('services')
from excel_processor import AdvancedExcelProcessor, ExcelProcessingError
from inventory_service import AdvancedInventoryManager
from analytics_engine import RealTimeAnalyticsEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AutomationJob:
    """Data class for automation job configuration"""
    job_id: str
    job_name: str
    job_type: str
    schedule: str  # cron-like schedule
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    success_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None

@dataclass
class DataSyncResult:
    """Result of data synchronization operation"""
    source: str
    target: str
    records_processed: int
    records_updated: int
    records_added: int
    records_errors: int
    duration_seconds: float
    success: bool
    error_message: Optional[str] = None

class DataAutomationEngine:
    """
    Comprehensive data automation system for Derivco facilities management
    Handles automated data processing, validation, synchronization, and maintenance
    """

    def __init__(self, excel_processor: AdvancedExcelProcessor = None):
        self.excel_processor = excel_processor or AdvancedExcelProcessor()
        self.automation_jobs: Dict[str, AutomationJob] = {}
        self.job_history: List[Dict[str, Any]] = []
        self.is_running = False
        self.scheduler_thread = None

        # Data validation rules
        self.validation_rules = self._load_validation_rules()

        # File monitoring
        self.monitored_files = {}
        self.file_checksums = {}

        # Setup automation directories
        self._setup_directories()

        # Load saved configuration
        self._load_automation_config()

    def _setup_directories(self):
        """Setup required directories"""
        directories = [
            'automation/logs',
            'automation/archives',
            'automation/temp',
            'automation/exports',
            'automation/imports'
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load data validation rules"""
        return {
            'inventory': {
                'required_fields': ['Item Code', 'Item Name', 'Quantity', 'Unit Price'],
                'field_types': {
                    'Quantity': 'int',
                    'Unit Price': 'float',
                    'Total Value': 'float'
                },
                'validation_functions': {
                    'Quantity': lambda x: x >= 0,
                    'Unit Price': lambda x: x >= 0,
                    'Item Code': lambda x: len(str(x).strip()) > 0,
                    'Item Name': lambda x: len(str(x).strip()) > 0
                }
            },
            'signout': {
                'required_fields': ['Item_Name', 'Borrower_Name', 'Date_Out'],
                'field_types': {
                    'Date_Out': 'datetime',
                    'Date_In': 'datetime',
                    'Expected_Return': 'datetime'
                },
                'validation_functions': {
                    'Item_Name': lambda x: len(str(x).strip()) > 0,
                    'Borrower_Name': lambda x: len(str(x).strip()) > 0,
                    'Date_Out': lambda x: pd.notna(x)
                }
            },
            'medical': {
                'required_fields': ['Item_Name', 'Stock_Level'],
                'field_types': {
                    'Stock_Level': 'int',
                    'Expiry_Date': 'datetime'
                },
                'validation_functions': {
                    'Stock_Level': lambda x: x >= 0,
                    'Item_Name': lambda x: len(str(x).strip()) > 0
                }
            }
        }

    def _load_automation_config(self):
        """Load automation configuration from file"""
        try:
            config_file = Path('automation/automation_config.json')
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)

                # Load jobs
                for job_data in config.get('jobs', []):
                    job = AutomationJob(**job_data)
                    if job.last_run:
                        job.last_run = datetime.fromisoformat(job.last_run)
                    if job.next_run:
                        job.next_run = datetime.fromisoformat(job.next_run)
                    self.automation_jobs[job.job_id] = job

                # Load job history
                self.job_history = config.get('job_history', [])

                logger.info(f"Loaded automation configuration with {len(self.automation_jobs)} jobs")

        except Exception as e:
            logger.warning(f"Could not load automation config: {e}")
            self._setup_default_jobs()

    def _setup_default_jobs(self):
        """Setup default automation jobs"""
        default_jobs = [
            AutomationJob(
                job_id='daily_data_validation',
                job_name='Daily Data Validation',
                job_type='validation',
                schedule='daily_08:00',
                enabled=True
            ),
            AutomationJob(
                job_id='hourly_file_monitoring',
                job_name='File Change Monitoring',
                job_type='monitoring',
                schedule='hourly',
                enabled=True
            ),
            AutomationJob(
                job_id='weekly_data_cleanup',
                job_name='Weekly Data Cleanup',
                job_type='cleanup',
                schedule='weekly_sunday_02:00',
                enabled=True
            ),
            AutomationJob(
                job_id='daily_backup',
                job_name='Daily Data Backup',
                job_type='backup',
                schedule='daily_23:00',
                enabled=True
            ),
            AutomationJob(
                job_id='compliance_monitoring',
                job_name='Compliance Monitoring',
                job_type='compliance',
                schedule='every_4_hours',
                enabled=True
            )
        ]

        for job in default_jobs:
            self.automation_jobs[job.job_id] = job

        logger.info(f"Setup {len(default_jobs)} default automation jobs")

    def _save_automation_config(self):
        """Save automation configuration to file"""
        try:
            config = {
                'jobs': [],
                'job_history': self.job_history[-1000:]  # Keep last 1000 entries
            }

            # Convert jobs to serializable format
            for job in self.automation_jobs.values():
                job_data = {
                    'job_id': job.job_id,
                    'job_name': job.job_name,
                    'job_type': job.job_type,
                    'schedule': job.schedule,
                    'enabled': job.enabled,
                    'last_run': job.last_run.isoformat() if job.last_run else None,
                    'next_run': job.next_run.isoformat() if job.next_run else None,
                    'success_count': job.success_count,
                    'error_count': job.error_count,
                    'last_error': job.last_error
                }
                config['jobs'].append(job_data)

            config_file = Path('automation/automation_config.json')
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info("Automation configuration saved")

        except Exception as e:
            logger.error(f"Error saving automation config: {e}")

    def validate_data_file(self, file_type: str, file_path: str = None) -> Dict[str, Any]:
        """
        Comprehensive data validation for Excel files
        Returns detailed validation report
        """
        try:
            logger.info(f"Validating {file_type} data...")

            validation_result = {
                'file_type': file_type,
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'is_valid': True,
                'total_records': 0,
                'valid_records': 0,
                'error_records': 0,
                'warnings': [],
                'errors': [],
                'field_statistics': {},
                'recommendations': []
            }

            # Load data
            if file_type in ['inventory', 'signout', 'medical']:
                df = self.excel_processor.read_excel_file(file_type)
            else:
                raise ValueError(f"Unknown file type: {file_type}")

            if df.empty:
                validation_result['errors'].append("No data found in file")
                validation_result['is_valid'] = False
                return validation_result

            validation_result['total_records'] = len(df)

            # Get validation rules for this file type
            rules = self.validation_rules.get(file_type, {})
            required_fields = rules.get('required_fields', [])
            field_types = rules.get('field_types', {})
            validation_functions = rules.get('validation_functions', {})

            # Check required fields
            missing_fields = [field for field in required_fields if field not in df.columns]
            if missing_fields:
                validation_result['errors'].append(f"Missing required fields: {missing_fields}")
                validation_result['is_valid'] = False

            # Validate field types and content
            valid_record_count = 0
            error_details = []

            for index, row in df.iterrows():
                record_valid = True
                record_errors = []

                # Check required field values
                for field in required_fields:
                    if field in df.columns:
                        value = row[field]
                        if pd.isna(value) or (isinstance(value, str) and not value.strip()):
                            record_errors.append(f"Row {index + 1}: Missing value for {field}")
                            record_valid = False

                # Apply validation functions
                for field, validation_func in validation_functions.items():
                    if field in df.columns:
                        value = row[field]
                        if not pd.isna(value):
                            try:
                                if not validation_func(value):
                                    record_errors.append(f"Row {index + 1}: Invalid value for {field}: {value}")
                                    record_valid = False
                            except Exception as e:
                                record_errors.append(f"Row {index + 1}: Validation error for {field}: {e}")
                                record_valid = False

                if record_valid:
                    valid_record_count += 1
                else:
                    error_details.extend(record_errors)

            validation_result['valid_records'] = valid_record_count
            validation_result['error_records'] = len(df) - valid_record_count

            if error_details:
                validation_result['errors'].extend(error_details[:50])  # Limit to first 50 errors
                if len(error_details) > 50:
                    validation_result['warnings'].append(f"Additional {len(error_details) - 50} validation errors not shown")

            # Generate field statistics
            for column in df.columns:
                if column in df.select_dtypes(include=[np.number]).columns:
                    validation_result['field_statistics'][column] = {
                        'min': float(df[column].min()) if not df[column].empty else None,
                        'max': float(df[column].max()) if not df[column].empty else None,
                        'mean': float(df[column].mean()) if not df[column].empty else None,
                        'null_count': int(df[column].isnull().sum())
                    }
                else:
                    validation_result['field_statistics'][column] = {
                        'unique_values': int(df[column].nunique()),
                        'null_count': int(df[column].isnull().sum()),
                        'most_common': str(df[column].mode().iloc[0]) if not df[column].empty else None
                    }

            # Generate recommendations
            if validation_result['error_records'] > 0:
                error_percentage = (validation_result['error_records'] / validation_result['total_records']) * 100
                if error_percentage > 10:
                    validation_result['recommendations'].append("High error rate detected. Consider data source review.")
                elif error_percentage > 5:
                    validation_result['recommendations'].append("Moderate error rate. Data cleanup recommended.")

                validation_result['recommendations'].append("Review validation errors and correct source data.")

            # Check for potential issues
            for column in df.columns:
                null_percentage = (df[column].isnull().sum() / len(df)) * 100
                if null_percentage > 20:
                    validation_result['warnings'].append(f"{column} has {null_percentage:.1f}% missing values")

            # Final validation status
            if validation_result['error_records'] > 0:
                validation_result['is_valid'] = False

            logger.info(f"Data validation completed: {validation_result['valid_records']}/{validation_result['total_records']} valid records")

            return validation_result

        except Exception as e:
            logger.error(f"Error validating data file: {e}")
            return {
                'file_type': file_type,
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'is_valid': False,
                'error': str(e)
            }

    def synchronize_data(self, source_type: str, target_type: str = 'database') -> DataSyncResult:
        """
        Synchronize data between different sources
        Currently supports Excel to internal format synchronization
        """
        try:
            start_time = datetime.now()
            logger.info(f"Synchronizing data from {source_type} to {target_type}")

            result = DataSyncResult(
                source=source_type,
                target=target_type,
                records_processed=0,
                records_updated=0,
                records_added=0,
                records_errors=0,
                duration_seconds=0,
                success=False
            )

            # Load source data
            source_df = self.excel_processor.read_excel_file(source_type)
            if source_df.empty:
                result.error_message = "No data found in source"
                return result

            result.records_processed = len(source_df)

            # Validate source data
            validation_result = self.validate_data_file(source_type)
            if not validation_result['is_valid']:
                result.records_errors = validation_result['error_records']
                result.error_message = f"Source data validation failed: {len(validation_result['errors'])} errors"
                return result

            # For now, synchronization means ensuring data integrity
            # In production, this would sync with actual database
            result.records_added = result.records_processed
            result.success = True

            # Calculate duration
            end_time = datetime.now()
            result.duration_seconds = (end_time - start_time).total_seconds()

            logger.info(f"Data synchronization completed: {result.records_processed} records processed in {result.duration_seconds:.2f}s")

            return result

        except Exception as e:
            logger.error(f"Error synchronizing data: {e}")
            result = DataSyncResult(
                source=source_type,
                target=target_type,
                records_processed=0,
                records_updated=0,
                records_added=0,
                records_errors=0,
                duration_seconds=0,
                success=False,
                error_message=str(e)
            )
            return result

    def monitor_file_changes(self) -> Dict[str, Any]:
        """
        Monitor Excel files for changes and trigger updates
        Returns monitoring report
        """
        try:
            logger.info("Monitoring file changes...")

            monitoring_result = {
                'timestamp': datetime.now().isoformat(),
                'files_monitored': 0,
                'files_changed': 0,
                'changes_detected': [],
                'errors': []
            }

            # Files to monitor
            files_to_monitor = {
                'inventory': self.excel_processor.config['inventory'].filename,
                'signout': self.excel_processor.config['signout'].filename,
                'medical': self.excel_processor.config['medical'].filename
            }

            for file_type, filename in files_to_monitor.items():
                try:
                    file_path = Path(filename)
                    if not file_path.exists():
                        monitoring_result['errors'].append(f"{filename} not found")
                        continue

                    monitoring_result['files_monitored'] += 1

                    # Calculate file checksum
                    current_checksum = self._calculate_file_checksum(file_path)
                    previous_checksum = self.file_checksums.get(str(file_path))

                    if previous_checksum and previous_checksum != current_checksum:
                        # File has changed
                        monitoring_result['files_changed'] += 1
                        monitoring_result['changes_detected'].append({
                            'file': filename,
                            'file_type': file_type,
                            'change_detected_at': datetime.now().isoformat(),
                            'previous_checksum': previous_checksum,
                            'current_checksum': current_checksum
                        })

                        # Trigger data validation for changed file
                        logger.info(f"Change detected in {filename}, triggering validation...")
                        validation_result = self.validate_data_file(file_type)

                        if not validation_result['is_valid']:
                            monitoring_result['errors'].append(
                                f"{filename} validation failed after change: {len(validation_result['errors'])} errors"
                            )

                    # Update stored checksum
                    self.file_checksums[str(file_path)] = current_checksum

                except Exception as e:
                    monitoring_result['errors'].append(f"Error monitoring {filename}: {str(e)}")

            logger.info(f"File monitoring completed: {monitoring_result['files_changed']}/{monitoring_result['files_monitored']} files changed")

            return monitoring_result

        except Exception as e:
            logger.error(f"Error in file monitoring: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path}: {e}")
            return ""

    def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """
        Clean up old data files and archives
        Returns cleanup report
        """
        try:
            logger.info(f"Cleaning up data older than {days_to_keep} days...")

            cleanup_result = {
                'timestamp': datetime.now().isoformat(),
                'directories_cleaned': 0,
                'files_deleted': 0,
                'space_freed_mb': 0,
                'errors': []
            }

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # Directories to clean
            cleanup_dirs = [
                'automation/logs',
                'automation/archives',
                'automation/temp',
                'reports'
            ]

            for directory in cleanup_dirs:
                try:
                    dir_path = Path(directory)
                    if not dir_path.exists():
                        continue

                    cleanup_result['directories_cleaned'] += 1
                    files_deleted = 0
                    space_freed = 0

                    for file_path in dir_path.rglob('*'):
                        if file_path.is_file():
                            file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
                            if file_date < cutoff_date:
                                file_size = file_path.stat().st_size
                                file_path.unlink()
                                files_deleted += 1
                                space_freed += file_size

                    cleanup_result['files_deleted'] += files_deleted
                    cleanup_result['space_freed_mb'] += space_freed / (1024 * 1024)

                except Exception as e:
                    cleanup_result['errors'].append(f"Error cleaning {directory}: {str(e)}")

            logger.info(f"Cleanup completed: {cleanup_result['files_deleted']} files deleted, "
                       f"{cleanup_result['space_freed_mb']:.2f}MB freed")

            return cleanup_result

        except Exception as e:
            logger.error(f"Error in data cleanup: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def backup_data(self, backup_location: str = None) -> Dict[str, Any]:
        """
        Create comprehensive backup of all data files
        Returns backup report
        """
        try:
            if not backup_location:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_location = f'automation/backups/backup_{timestamp}'

            logger.info(f"Creating data backup at {backup_location}")

            backup_result = {
                'timestamp': datetime.now().isoformat(),
                'backup_location': backup_location,
                'files_backed_up': 0,
                'total_size_mb': 0,
                'errors': []
            }

            # Create backup directory
            backup_path = Path(backup_location)
            backup_path.mkdir(parents=True, exist_ok=True)

            # Files to backup
            files_to_backup = [
                'STORES_INFRASTRUCTURE_ADMINISTRATION_enhanced.xlsx',
                'signout_data_improved.xlsx',
                'medication_data_enhanced.xlsx',
                'automation/automation_config.json',
                'analytics_history.json'
            ]

            # Also backup any recent reports
            reports_dir = Path('reports')
            if reports_dir.exists():
                recent_reports = []
                for report_file in reports_dir.glob('*'):
                    if report_file.is_file():
                        file_age = datetime.now() - datetime.fromtimestamp(report_file.stat().st_mtime)
                        if file_age.days <= 7:  # Backup reports from last 7 days
                            recent_reports.append(str(report_file))
                files_to_backup.extend(recent_reports)

            for file_path_str in files_to_backup:
                try:
                    source_path = Path(file_path_str)
                    if not source_path.exists():
                        continue

                    # Create backup file path
                    backup_file_path = backup_path / source_path.name

                    # Copy file
                    shutil.copy2(source_path, backup_file_path)

                    backup_result['files_backed_up'] += 1
                    backup_result['total_size_mb'] += source_path.stat().st_size / (1024 * 1024)

                except Exception as e:
                    backup_result['errors'].append(f"Error backing up {file_path_str}: {str(e)}")

            logger.info(f"Backup completed: {backup_result['files_backed_up']} files, "
                       f"{backup_result['total_size_mb']:.2f}MB")

            return backup_result

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def run_automation_job(self, job_id: str) -> Dict[str, Any]:
        """
        Run a specific automation job
        Returns job execution result
        """
        try:
            if job_id not in self.automation_jobs:
                raise ValueError(f"Job {job_id} not found")

            job = self.automation_jobs[job_id]
            if not job.enabled:
                return {
                    'job_id': job_id,
                    'status': 'skipped',
                    'message': 'Job is disabled'
                }

            logger.info(f"Running automation job: {job.job_name}")

            start_time = datetime.now()
            job_result = {
                'job_id': job_id,
                'job_name': job.job_name,
                'job_type': job.job_type,
                'start_time': start_time.isoformat(),
                'status': 'running',
                'result': {},
                'error': None
            }

            # Execute job based on type
            if job.job_type == 'validation':
                # Run validation on all data files
                validation_results = {}
                for file_type in ['inventory', 'signout', 'medical']:
                    validation_results[file_type] = self.validate_data_file(file_type)
                job_result['result'] = validation_results

            elif job.job_type == 'monitoring':
                # Run file monitoring
                monitoring_result = self.monitor_file_changes()
                job_result['result'] = monitoring_result

            elif job.job_type == 'cleanup':
                # Run data cleanup
                cleanup_result = self.cleanup_old_data()
                job_result['result'] = cleanup_result

            elif job.job_type == 'backup':
                # Run data backup
                backup_result = self.backup_data()
                job_result['result'] = backup_result

            elif job.job_type == 'compliance':
                # Run compliance monitoring (if analytics engine available)
                # This would integrate with analytics engine in production
                job_result['result'] = {
                    'message': 'Compliance monitoring would run here with analytics engine integration'
                }

            else:
                raise ValueError(f"Unknown job type: {job.job_type}")

            # Update job status
            end_time = datetime.now()
            job_result['end_time'] = end_time.isoformat()
            job_result['duration_seconds'] = (end_time - start_time).total_seconds()
            job_result['status'] = 'completed'

            # Update job tracking
            job.last_run = start_time
            job.success_count += 1
            job.last_error = None

            logger.info(f"Automation job {job.job_name} completed successfully in {job_result['duration_seconds']:.2f}s")

            return job_result

        except Exception as e:
            logger.error(f"Error running automation job {job_id}: {e}")

            # Update job error tracking
            if job_id in self.automation_jobs:
                job = self.automation_jobs[job_id]
                job.error_count += 1
                job.last_error = str(e)

            return {
                'job_id': job_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

        finally:
            # Save configuration after job run
            self._save_automation_config()

    def run_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Run all enabled automation jobs
        Returns list of job results
        """
        results = []

        logger.info(f"Running all enabled automation jobs ({len([j for j in self.automation_jobs.values() if j.enabled])} jobs)")

        # Use thread pool for parallel execution of independent jobs
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_job = {
                executor.submit(self.run_automation_job, job_id): job_id
                for job_id, job in self.automation_jobs.items()
                if job.enabled
            }

            for future in as_completed(future_to_job):
                job_id = future_to_job[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Job {job_id} failed: {e}")
                    results.append({
                        'job_id': job_id,
                        'status': 'failed',
                        'error': str(e)
                    })

        logger.info(f"All automation jobs completed: {len(results)} jobs executed")
        return results

    def start_scheduler(self):
        """Start the automation scheduler"""
        try:
            if self.is_running:
                logger.warning("Scheduler already running")
                return

            logger.info("Starting automation scheduler...")

            # Setup scheduled jobs
            schedule.every().hour.do(lambda: self.run_automation_job('hourly_file_monitoring'))
            schedule.every().day.at("08:00").do(lambda: self.run_automation_job('daily_data_validation'))
            schedule.every().day.at("23:00").do(lambda: self.run_automation_job('daily_backup'))
            schedule.every().sunday.at("02:00").do(lambda: self.run_automation_job('weekly_data_cleanup'))
            schedule.every(4).hours.do(lambda: self.run_automation_job('compliance_monitoring'))

            # Start scheduler in separate thread
            self.is_running = True

            def run_scheduler():
                while self.is_running:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute

            self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            self.scheduler_thread.start()

            logger.info("Automation scheduler started successfully")

        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            self.is_running = False

    def stop_scheduler(self):
        """Stop the automation scheduler"""
        try:
            logger.info("Stopping automation scheduler...")
            self.is_running = False

            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)

            schedule.clear()
            logger.info("Automation scheduler stopped")

        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")

    def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation system status"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'scheduler_running': self.is_running,
                'total_jobs': len(self.automation_jobs),
                'enabled_jobs': len([j for j in self.automation_jobs.values() if j.enabled]),
                'jobs': {},
                'system_health': 'healthy'
            }

            # Job status
            for job_id, job in self.automation_jobs.items():
                status['jobs'][job_id] = {
                    'name': job.job_name,
                    'type': job.job_type,
                    'enabled': job.enabled,
                    'last_run': job.last_run.isoformat() if job.last_run else None,
                    'success_count': job.success_count,
                    'error_count': job.error_count,
                    'last_error': job.last_error
                }

            # Determine system health
            total_errors = sum(job.error_count for job in self.automation_jobs.values())
            if total_errors > 10:
                status['system_health'] = 'degraded'
            elif total_errors > 5:
                status['system_health'] = 'warning'

            return status

        except Exception as e:
            logger.error(f"Error getting automation status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'system_health': 'error'
            }

    def generate_automation_report(self) -> Dict[str, Any]:
        """Generate comprehensive automation report"""
        try:
            logger.info("Generating automation report...")

            report = {
                'timestamp': datetime.now().isoformat(),
                'report_period': '30_days',
                'summary': {},
                'job_performance': {},
                'data_quality_trends': {},
                'recommendations': []
            }

            # Summary statistics
            total_jobs = len(self.automation_jobs)
            enabled_jobs = len([j for j in self.automation_jobs.values() if j.enabled])
            total_successes = sum(job.success_count for job in self.automation_jobs.values())
            total_errors = sum(job.error_count for job in self.automation_jobs.values())

            report['summary'] = {
                'total_jobs_configured': total_jobs,
                'enabled_jobs': enabled_jobs,
                'total_successful_runs': total_successes,
                'total_failed_runs': total_errors,
                'success_rate': (total_successes / (total_successes + total_errors) * 100) if (total_successes + total_errors) > 0 else 0,
                'scheduler_status': 'running' if self.is_running else 'stopped'
            }

            # Individual job performance
            for job_id, job in self.automation_jobs.items():
                success_rate = (job.success_count / (job.success_count + job.error_count) * 100) if (job.success_count + job.error_count) > 0 else 0

                report['job_performance'][job_id] = {
                    'job_name': job.job_name,
                    'job_type': job.job_type,
                    'enabled': job.enabled,
                    'success_count': job.success_count,
                    'error_count': job.error_count,
                    'success_rate': success_rate,
                    'last_run': job.last_run.isoformat() if job.last_run else None,
                    'last_error': job.last_error
                }

            # Generate recommendations
            if report['summary']['success_rate'] < 90:
                report['recommendations'].append({
                    'priority': 'high',
                    'category': 'reliability',
                    'description': 'Automation success rate below 90%. Review job configurations and error logs.'
                })

            if not self.is_running:
                report['recommendations'].append({
                    'priority': 'critical',
                    'category': 'availability',
                    'description': 'Automation scheduler is not running. Start scheduler to enable automated jobs.'
                })

            jobs_with_errors = [job for job in self.automation_jobs.values() if job.error_count > 0]
            if jobs_with_errors:
                report['recommendations'].append({
                    'priority': 'medium',
                    'category': 'maintenance',
                    'description': f'{len(jobs_with_errors)} jobs have reported errors. Review and address error conditions.'
                })

            logger.info("Automation report generated successfully")
            return report

        except Exception as e:
            logger.error(f"Error generating automation report: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }