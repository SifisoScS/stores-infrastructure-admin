#!/usr/bin/env python3
"""
Comprehensive Notification System for Derivco Facilities Management
Handles email alerts, SMS notifications, dashboard alerts, and escalation procedures
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from pathlib import Path
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import uuid
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types of notifications"""
    EMAIL = "email"
    SMS = "sms"
    DASHBOARD = "dashboard"
    SYSTEM = "system"
    ESCALATION = "escalation"

class NotificationPriority(Enum):
    """Notification priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class NotificationTemplate:
    """Data class for notification templates"""
    template_id: str
    template_name: str
    notification_type: NotificationType
    subject_template: str
    body_template: str
    priority: NotificationPriority
    enabled: bool = True
    created_date: datetime = field(default_factory=datetime.now)
    usage_count: int = 0

@dataclass
class NotificationRecipient:
    """Data class for notification recipients"""
    recipient_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "user"
    department: str = "facilities"
    notification_preferences: Dict[str, bool] = field(default_factory=lambda: {
        'email_enabled': True,
        'sms_enabled': False,
        'dashboard_enabled': True,
        'critical_alerts': True,
        'daily_digest': True
    })
    active: bool = True

@dataclass
class NotificationMessage:
    """Data class for notification messages"""
    message_id: str
    notification_type: NotificationType
    priority: NotificationPriority
    recipients: List[str]
    subject: str
    body: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_date: datetime = field(default_factory=datetime.now)
    scheduled_date: Optional[datetime] = None
    sent_date: Optional[datetime] = None
    status: NotificationStatus = NotificationStatus.PENDING
    delivery_attempts: int = 0
    error_message: Optional[str] = None
    attachments: List[str] = field(default_factory=list)

class NotificationSystem:
    """
    Comprehensive notification system for Derivco facilities management
    Handles multi-channel notifications with templates, escalation, and delivery tracking
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.templates: Dict[str, NotificationTemplate] = {}
        self.recipients: Dict[str, NotificationRecipient] = {}
        self.messages: Dict[str, NotificationMessage] = {}
        self.message_queue = queue.Queue()
        self.delivery_history: List[Dict[str, Any]] = []

        # Notification processing
        self.is_processing = False
        self.processor_thread = None

        # Setup notification system
        self._setup_default_templates()
        self._setup_default_recipients()
        self._load_system_config()

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default notification configuration"""
        return {
            'email': {
                'smtp_server': 'smtp.office365.com',  # Derivco likely uses Office 365
                'smtp_port': 587,
                'use_tls': True,
                'username': '',  # To be configured
                'password': '',  # To be configured
                'from_address': 'facilities@derivco.co.za',
                'from_name': 'Derivco Facilities Management'
            },
            'sms': {
                'provider': 'twilio',  # Or local SA provider
                'account_sid': '',
                'auth_token': '',
                'from_number': '',
                'enabled': False
            },
            'system': {
                'max_retry_attempts': 3,
                'retry_delay_minutes': 5,
                'batch_size': 10,
                'enable_digest': True,
                'digest_time': '08:00',
                'enable_escalation': True,
                'escalation_delay_hours': 2
            },
            'derivco_specific': {
                'facilities_manager_email': 'facilities.manager@derivco.co.za',
                'head_of_facilities_email': 'head.facilities@derivco.co.za',
                'it_support_email': 'it.support@derivco.co.za',
                'emergency_contact': '+27-xx-xxx-xxxx'
            }
        }

    def _setup_default_templates(self):
        """Setup default notification templates"""
        default_templates = [
            NotificationTemplate(
                template_id="CRITICAL_STOCK_ALERT",
                template_name="Critical Stock Level Alert",
                notification_type=NotificationType.EMAIL,
                subject_template="URGENT: Critical Stock Alert - {item_name}",
                body_template="""
                <h2>Critical Stock Level Alert</h2>
                <p><strong>Item:</strong> {item_name} ({item_code})</p>
                <p><strong>Current Stock:</strong> {current_stock} units</p>
                <p><strong>Reorder Level:</strong> {reorder_level} units</p>
                <p><strong>Supplier:</strong> {supplier}</p>
                <p><strong>Category:</strong> {category}</p>

                <p><strong>Action Required:</strong> Immediate reordering recommended to prevent stockout.</p>

                <p>Please review and take appropriate action.</p>

                <hr>
                <p><em>Derivco Facilities Management System</em><br>
                Generated: {timestamp}</p>
                """,
                priority=NotificationPriority.CRITICAL
            ),
            NotificationTemplate(
                template_id="OVERDUE_EQUIPMENT",
                template_name="Overdue Equipment Return",
                notification_type=NotificationType.EMAIL,
                subject_template="Overdue Equipment Return - {item_name}",
                body_template="""
                <h2>Overdue Equipment Return Notice</h2>
                <p><strong>Borrower:</strong> {borrower_name}</p>
                <p><strong>Item:</strong> {item_name}</p>
                <p><strong>Date Borrowed:</strong> {date_out}</p>
                <p><strong>Expected Return:</strong> {expected_return}</p>
                <p><strong>Days Overdue:</strong> {days_overdue}</p>

                <p><strong>Please return the equipment immediately.</strong></p>

                <p>If you are unable to return the equipment, please contact the Facilities team immediately.</p>

                <hr>
                <p><em>Derivco Facilities Management System</em></p>
                """,
                priority=NotificationPriority.HIGH
            ),
            NotificationTemplate(
                template_id="COMPLIANCE_VIOLATION",
                template_name="Compliance Violation Alert",
                notification_type=NotificationType.EMAIL,
                subject_template="Compliance Violation Detected - {violation_type}",
                body_template="""
                <h2>Compliance Violation Alert</h2>
                <p><strong>Violation Type:</strong> {violation_type}</p>
                <p><strong>Current Compliance Level:</strong> {compliance_percentage}%</p>
                <p><strong>Target Compliance Level:</strong> {target_percentage}%</p>
                <p><strong>Risk Level:</strong> {risk_level}</p>

                <p><strong>Details:</strong> {violation_details}</p>

                <p><strong>Immediate Action Required:</strong> Please review and implement corrective measures.</p>

                <p>Recommended Actions:</p>
                <ul>
                {recommended_actions}
                </ul>

                <hr>
                <p><em>Derivco Facilities Management System</em></p>
                """,
                priority=NotificationPriority.CRITICAL
            ),
            NotificationTemplate(
                template_id="DAILY_DIGEST",
                template_name="Daily Facilities Digest",
                notification_type=NotificationType.EMAIL,
                subject_template="Daily Facilities Digest - {date}",
                body_template="""
                <h2>Daily Facilities Management Digest</h2>
                <p><strong>Date:</strong> {date}</p>

                <h3>Inventory Summary</h3>
                <ul>
                    <li>Total Items: {total_items}</li>
                    <li>Total Value: R{total_value:,.2f}</li>
                    <li>Low Stock Items: {low_stock_count}</li>
                    <li>Critical Stock Items: {critical_stock_count}</li>
                </ul>

                <h3>Sign-Out Activity</h3>
                <ul>
                    <li>Items Checked Out: {items_checked_out}</li>
                    <li>Items Returned: {items_returned}</li>
                    <li>Outstanding Items: {outstanding_items}</li>
                    <li>Overdue Items: {overdue_items}</li>
                </ul>

                <h3>Compliance Status</h3>
                <ul>
                    <li>Work Order Compliance: {wo_compliance}%</li>
                    <li>Tool Return Compliance: {return_compliance}%</li>
                    <li>Overall Risk Level: {risk_level}</li>
                </ul>

                <h3>Action Items</h3>
                {action_items}

                <hr>
                <p><em>Derivco Facilities Management System</em></p>
                """,
                priority=NotificationPriority.MEDIUM
            ),
            NotificationTemplate(
                template_id="APPROVAL_REQUEST",
                template_name="Approval Request Notification",
                notification_type=NotificationType.EMAIL,
                subject_template="Approval Required - {request_type}",
                body_template="""
                <h2>Approval Request</h2>
                <p><strong>Request Type:</strong> {request_type}</p>
                <p><strong>Requester:</strong> {requester_name}</p>
                <p><strong>Request Date:</strong> {request_date}</p>

                <h3>Request Details</h3>
                {request_details}

                <h3>Justification</h3>
                <p>{justification}</p>

                <p><strong>Priority:</strong> {priority}</p>

                <p>Please review and approve/reject this request at your earliest convenience.</p>

                <p><a href="{approval_link}">Review Request</a></p>

                <hr>
                <p><em>Derivco Facilities Management System</em></p>
                """,
                priority=NotificationPriority.HIGH
            ),
            NotificationTemplate(
                template_id="SYSTEM_MAINTENANCE",
                template_name="System Maintenance Notification",
                notification_type=NotificationType.EMAIL,
                subject_template="Scheduled Maintenance - {maintenance_type}",
                body_template="""
                <h2>System Maintenance Notification</h2>
                <p><strong>Maintenance Type:</strong> {maintenance_type}</p>
                <p><strong>Scheduled Date:</strong> {maintenance_date}</p>
                <p><strong>Duration:</strong> {duration}</p>

                <p><strong>Impact:</strong> {impact_description}</p>

                <p><strong>What to Expect:</strong></p>
                <ul>
                {maintenance_details}
                </ul>

                <p>We apologize for any inconvenience and appreciate your patience.</p>

                <hr>
                <p><em>Derivco IT & Facilities Team</em></p>
                """,
                priority=NotificationPriority.MEDIUM
            )
        ]

        for template in default_templates:
            self.templates[template.template_id] = template

        logger.info(f"Setup {len(default_templates)} notification templates")

    def _setup_default_recipients(self):
        """Setup default notification recipients"""
        default_recipients = [
            NotificationRecipient(
                recipient_id="facilities_manager",
                name="Facilities Manager",
                email="facilities.manager@derivco.co.za",
                role="manager",
                department="facilities",
                notification_preferences={
                    'email_enabled': True,
                    'sms_enabled': True,
                    'dashboard_enabled': True,
                    'critical_alerts': True,
                    'daily_digest': True
                }
            ),
            NotificationRecipient(
                recipient_id="facilities_assistant",
                name="Facilities Assistant",
                email="facilities.assistant@derivco.co.za",
                role="assistant",
                department="facilities",
                notification_preferences={
                    'email_enabled': True,
                    'sms_enabled': False,
                    'dashboard_enabled': True,
                    'critical_alerts': True,
                    'daily_digest': False
                }
            ),
            NotificationRecipient(
                recipient_id="head_of_facilities",
                name="Head of Facilities",
                email="head.facilities@derivco.co.za",
                role="head",
                department="facilities",
                notification_preferences={
                    'email_enabled': True,
                    'sms_enabled': True,
                    'dashboard_enabled': True,
                    'critical_alerts': True,
                    'daily_digest': True
                }
            ),
            NotificationRecipient(
                recipient_id="it_support",
                name="IT Support",
                email="it.support@derivco.co.za",
                role="support",
                department="it",
                notification_preferences={
                    'email_enabled': True,
                    'sms_enabled': False,
                    'dashboard_enabled': False,
                    'critical_alerts': True,
                    'daily_digest': False
                }
            ),
            NotificationRecipient(
                recipient_id="sifiso_shezi",
                name="Sifiso Cyprian Shezi",
                email="sifiso.shezi@derivco.co.za",
                role="assistant",
                department="facilities",
                notification_preferences={
                    'email_enabled': True,
                    'sms_enabled': True,
                    'dashboard_enabled': True,
                    'critical_alerts': True,
                    'daily_digest': True
                }
            )
        ]

        for recipient in default_recipients:
            self.recipients[recipient.recipient_id] = recipient

        logger.info(f"Setup {len(default_recipients)} notification recipients")

    def _load_system_config(self):
        """Load system configuration from file"""
        try:
            config_file = Path('notifications/notification_config.json')
            if config_file.exists():
                with open(config_file, 'r') as f:
                    saved_config = json.load(f)

                # Update configuration
                self.config.update(saved_config.get('config', {}))

                # Load custom templates
                for template_data in saved_config.get('custom_templates', []):
                    template = NotificationTemplate(**template_data)
                    self.templates[template.template_id] = template

                # Load custom recipients
                for recipient_data in saved_config.get('custom_recipients', []):
                    recipient = NotificationRecipient(**recipient_data)
                    self.recipients[recipient.recipient_id] = recipient

                logger.info("Loaded notification system configuration")

        except Exception as e:
            logger.warning(f"Could not load notification config: {e}")

    def create_notification(self, template_id: str, recipients: List[str],
                          template_data: Dict[str, Any],
                          priority: NotificationPriority = None,
                          scheduled_date: datetime = None) -> str:
        """
        Create a new notification message
        Returns the message ID
        """
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} not found")

            template = self.templates[template_id]
            if not template.enabled:
                raise ValueError(f"Template {template_id} is disabled")

            # Generate message ID
            message_id = f"MSG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            # Process template
            subject = self._process_template_string(template.subject_template, template_data)
            body = self._process_template_string(template.body_template, template_data)

            # Create notification message
            message = NotificationMessage(
                message_id=message_id,
                notification_type=template.notification_type,
                priority=priority or template.priority,
                recipients=recipients,
                subject=subject,
                body=body,
                metadata=template_data,
                scheduled_date=scheduled_date
            )

            self.messages[message_id] = message

            # Add to processing queue
            self.message_queue.put(message_id)

            # Update template usage
            template.usage_count += 1

            logger.info(f"Created notification {message_id} using template {template_id}")

            return message_id

        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise

    def _process_template_string(self, template_string: str, data: Dict[str, Any]) -> str:
        """Process template string with data substitution"""
        try:
            # Add common variables
            data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data['date'] = datetime.now().strftime('%Y-%m-%d')
            data['time'] = datetime.now().strftime('%H:%M:%S')

            # Handle list-type data for HTML formatting
            for key, value in data.items():
                if isinstance(value, list):
                    if key.endswith('_actions') or key.endswith('_items') or key.endswith('_details'):
                        # Format as HTML list items
                        data[key] = '\n'.join([f'<li>{item}</li>' for item in value])
                    else:
                        # Format as comma-separated string
                        data[key] = ', '.join(str(item) for item in value)

            # Replace template variables
            processed_string = template_string.format(**data)

            return processed_string

        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            return template_string
        except Exception as e:
            logger.error(f"Error processing template: {e}")
            return template_string

    def send_critical_stock_alert(self, item_data: Dict[str, Any]) -> str:
        """Send critical stock alert notification"""
        try:
            # Determine recipients based on criticality
            recipients = ['facilities_manager', 'sifiso_shezi']

            if item_data.get('current_stock', 0) == 0:
                recipients.append('head_of_facilities')

            message_id = self.create_notification(
                template_id='CRITICAL_STOCK_ALERT',
                recipients=recipients,
                template_data=item_data,
                priority=NotificationPriority.CRITICAL
            )

            logger.info(f"Critical stock alert created: {message_id}")
            return message_id

        except Exception as e:
            logger.error(f"Error sending critical stock alert: {e}")
            raise

    def send_overdue_equipment_alert(self, equipment_data: Dict[str, Any]) -> str:
        """Send overdue equipment return alert"""
        try:
            recipients = ['facilities_manager']

            # Add borrower if email available
            borrower_email = equipment_data.get('borrower_email')
            if borrower_email:
                # Create temporary recipient for borrower
                borrower_id = f"temp_{equipment_data.get('borrower_name', 'unknown').lower().replace(' ', '_')}"
                self.recipients[borrower_id] = NotificationRecipient(
                    recipient_id=borrower_id,
                    name=equipment_data.get('borrower_name', 'Unknown'),
                    email=borrower_email,
                    role='employee',
                    active=True
                )
                recipients.append(borrower_id)

            # Escalate to head if severely overdue
            if equipment_data.get('days_overdue', 0) >= 14:
                recipients.append('head_of_facilities')

            message_id = self.create_notification(
                template_id='OVERDUE_EQUIPMENT',
                recipients=recipients,
                template_data=equipment_data,
                priority=NotificationPriority.HIGH
            )

            logger.info(f"Overdue equipment alert created: {message_id}")
            return message_id

        except Exception as e:
            logger.error(f"Error sending overdue equipment alert: {e}")
            raise

    def send_compliance_violation_alert(self, compliance_data: Dict[str, Any]) -> str:
        """Send compliance violation alert"""
        try:
            recipients = ['facilities_manager', 'head_of_facilities']

            # Add IT support for system-related compliance issues
            if compliance_data.get('violation_type', '').lower() in ['system', 'data']:
                recipients.append('it_support')

            message_id = self.create_notification(
                template_id='COMPLIANCE_VIOLATION',
                recipients=recipients,
                template_data=compliance_data,
                priority=NotificationPriority.CRITICAL
            )

            logger.info(f"Compliance violation alert created: {message_id}")
            return message_id

        except Exception as e:
            logger.error(f"Error sending compliance violation alert: {e}")
            raise

    def send_daily_digest(self, digest_data: Dict[str, Any]) -> str:
        """Send daily facilities digest"""
        try:
            # Send to recipients who have digest enabled
            recipients = [
                recipient_id for recipient_id, recipient in self.recipients.items()
                if recipient.notification_preferences.get('daily_digest', False) and recipient.active
            ]

            if not recipients:
                logger.info("No recipients configured for daily digest")
                return None

            message_id = self.create_notification(
                template_id='DAILY_DIGEST',
                recipients=recipients,
                template_data=digest_data,
                priority=NotificationPriority.MEDIUM
            )

            logger.info(f"Daily digest created: {message_id}")
            return message_id

        except Exception as e:
            logger.error(f"Error sending daily digest: {e}")
            raise

    def send_approval_request(self, approval_data: Dict[str, Any]) -> str:
        """Send approval request notification"""
        try:
            # Determine approver based on request type and value
            approver = approval_data.get('approver', 'facilities_manager')

            # Escalate high-value approvals
            if approval_data.get('estimated_value', 0) > 5000:
                approver = 'head_of_facilities'

            message_id = self.create_notification(
                template_id='APPROVAL_REQUEST',
                recipients=[approver],
                template_data=approval_data,
                priority=NotificationPriority.HIGH
            )

            logger.info(f"Approval request created: {message_id}")
            return message_id

        except Exception as e:
            logger.error(f"Error sending approval request: {e}")
            raise

    def process_notification_queue(self):
        """Process notifications in the queue"""
        try:
            processed_count = 0

            while not self.message_queue.empty():
                try:
                    message_id = self.message_queue.get_nowait()

                    if message_id in self.messages:
                        message = self.messages[message_id]

                        # Check if scheduled for future delivery
                        if message.scheduled_date and message.scheduled_date > datetime.now():
                            # Re-queue for later processing
                            self.message_queue.put(message_id)
                            continue

                        # Process message based on type
                        success = self._deliver_notification(message)

                        if success:
                            message.status = NotificationStatus.SENT
                            message.sent_date = datetime.now()
                            processed_count += 1
                        else:
                            message.delivery_attempts += 1
                            if message.delivery_attempts < self.config['system']['max_retry_attempts']:
                                # Re-queue for retry
                                self.message_queue.put(message_id)
                            else:
                                message.status = NotificationStatus.FAILED

                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"Error processing notification {message_id}: {e}")

            if processed_count > 0:
                logger.info(f"Processed {processed_count} notifications")

        except Exception as e:
            logger.error(f"Error processing notification queue: {e}")

    def _deliver_notification(self, message: NotificationMessage) -> bool:
        """Deliver a single notification message"""
        try:
            success_count = 0
            total_recipients = len(message.recipients)

            for recipient_id in message.recipients:
                if recipient_id not in self.recipients:
                    logger.warning(f"Recipient {recipient_id} not found")
                    continue

                recipient = self.recipients[recipient_id]
                if not recipient.active:
                    continue

                # Check recipient preferences
                if message.notification_type == NotificationType.EMAIL:
                    if recipient.notification_preferences.get('email_enabled', True) and recipient.email:
                        if self._send_email(recipient, message):
                            success_count += 1
                elif message.notification_type == NotificationType.SMS:
                    if recipient.notification_preferences.get('sms_enabled', False) and recipient.phone:
                        if self._send_sms(recipient, message):
                            success_count += 1

            # Consider successful if at least 50% of recipients received it
            success = success_count >= (total_recipients * 0.5)

            # Record delivery history
            delivery_record = {
                'message_id': message.message_id,
                'delivery_time': datetime.now().isoformat(),
                'total_recipients': total_recipients,
                'successful_deliveries': success_count,
                'success_rate': (success_count / total_recipients * 100) if total_recipients > 0 else 0,
                'overall_success': success
            }
            self.delivery_history.append(delivery_record)

            return success

        except Exception as e:
            logger.error(f"Error delivering notification {message.message_id}: {e}")
            message.error_message = str(e)
            return False

    def _send_email(self, recipient: NotificationRecipient, message: NotificationMessage) -> bool:
        """Send email notification"""
        try:
            if not self.config['email']['username'] or not self.config['email']['password']:
                logger.info("Email configuration incomplete - email not sent")
                return False

            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = f"{self.config['email']['from_name']} <{self.config['email']['from_address']}>"
            msg['To'] = recipient.email

            # Add HTML body
            html_body = MIMEText(message.body, 'html')
            msg.attach(html_body)

            # Add attachments if any
            for attachment_path in message.attachments:
                try:
                    with open(attachment_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())

                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {Path(attachment_path).name}',
                    )
                    msg.attach(part)
                except Exception as e:
                    logger.warning(f"Could not attach file {attachment_path}: {e}")

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port']) as server:
                if self.config['email']['use_tls']:
                    server.starttls(context=context)
                server.login(self.config['email']['username'], self.config['email']['password'])
                server.send_message(msg)

            logger.info(f"Email sent to {recipient.email} for message {message.message_id}")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {recipient.email}: {e}")
            return False

    def _send_sms(self, recipient: NotificationRecipient, message: NotificationMessage) -> bool:
        """Send SMS notification"""
        try:
            if not self.config['sms']['enabled'] or not self.config['sms']['account_sid']:
                logger.info("SMS configuration incomplete - SMS not sent")
                return False

            # For production implementation, integrate with Twilio or local SMS provider
            # This is a placeholder implementation

            sms_body = f"{message.subject}\n\n{self._strip_html(message.body)}"

            # Truncate to SMS length limit
            if len(sms_body) > 160:
                sms_body = sms_body[:157] + "..."

            logger.info(f"SMS would be sent to {recipient.phone}: {sms_body[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Error sending SMS to {recipient.phone}: {e}")
            return False

    def _strip_html(self, html_text: str) -> str:
        """Strip HTML tags from text"""
        try:
            import re
            clean = re.compile('<.*?>')
            return re.sub(clean, '', html_text).strip()
        except Exception:
            return html_text

    def start_notification_processor(self):
        """Start background notification processor"""
        try:
            if self.is_processing:
                logger.warning("Notification processor already running")
                return

            self.is_processing = True

            def process_notifications():
                while self.is_processing:
                    try:
                        self.process_notification_queue()
                        threading.Event().wait(30)  # Process every 30 seconds
                    except Exception as e:
                        logger.error(f"Error in notification processor: {e}")

            self.processor_thread = threading.Thread(target=process_notifications, daemon=True)
            self.processor_thread.start()

            logger.info("Notification processor started")

        except Exception as e:
            logger.error(f"Error starting notification processor: {e}")

    def stop_notification_processor(self):
        """Stop background notification processor"""
        try:
            self.is_processing = False
            if self.processor_thread and self.processor_thread.is_alive():
                self.processor_thread.join(timeout=5)
            logger.info("Notification processor stopped")
        except Exception as e:
            logger.error(f"Error stopping notification processor: {e}")

    def get_notification_statistics(self) -> Dict[str, Any]:
        """Get comprehensive notification statistics"""
        try:
            stats = {
                'timestamp': datetime.now().isoformat(),
                'system_status': {
                    'processor_running': self.is_processing,
                    'queue_size': self.message_queue.qsize(),
                    'total_templates': len(self.templates),
                    'active_recipients': len([r for r in self.recipients.values() if r.active])
                },
                'message_statistics': {
                    'total_messages': len(self.messages),
                    'pending_messages': len([m for m in self.messages.values() if m.status == NotificationStatus.PENDING]),
                    'sent_messages': len([m for m in self.messages.values() if m.status == NotificationStatus.SENT]),
                    'failed_messages': len([m for m in self.messages.values() if m.status == NotificationStatus.FAILED])
                },
                'template_usage': {},
                'delivery_performance': {}
            }

            # Template usage statistics
            for template_id, template in self.templates.items():
                stats['template_usage'][template_id] = {
                    'name': template.template_name,
                    'usage_count': template.usage_count,
                    'enabled': template.enabled
                }

            # Delivery performance (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_deliveries = [
                d for d in self.delivery_history
                if datetime.fromisoformat(d['delivery_time']) >= thirty_days_ago
            ]

            if recent_deliveries:
                stats['delivery_performance'] = {
                    'total_deliveries': len(recent_deliveries),
                    'average_success_rate': sum(d['success_rate'] for d in recent_deliveries) / len(recent_deliveries),
                    'total_recipients_reached': sum(d['successful_deliveries'] for d in recent_deliveries)
                }

            return stats

        except Exception as e:
            logger.error(f"Error generating notification statistics: {e}")
            return {'error': str(e)}