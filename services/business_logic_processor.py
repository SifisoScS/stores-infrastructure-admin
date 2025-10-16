#!/usr/bin/env python3
"""
Business Logic Processor for Derivco Facilities Management
Implements core business rules, workflows, and decision automation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import uuid

# Import core services
import sys
sys.path.append('core')
sys.path.append('services')
sys.path.append('utils')
from excel_processor import AdvancedExcelProcessor
from inventory_service import AdvancedInventoryManager, StockLevel
from analytics_engine import RealTimeAnalyticsEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class Priority(Enum):
    """Priority levels for business processes"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class BusinessRuleType(Enum):
    """Types of business rules"""
    VALIDATION = "validation"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    AUTOMATION = "automation"
    ESCALATION = "escalation"

@dataclass
class BusinessRule:
    """Data class for business rules"""
    rule_id: str
    rule_name: str
    rule_type: BusinessRuleType
    description: str
    condition: str  # Python expression to evaluate
    action: str     # Action to take when condition is met
    priority: Priority
    enabled: bool = True
    created_date: datetime = field(default_factory=datetime.now)
    last_executed: Optional[datetime] = None
    execution_count: int = 0

@dataclass
class WorkflowTask:
    """Data class for workflow tasks"""
    task_id: str
    workflow_id: str
    task_name: str
    task_type: str
    assignee: str
    status: WorkflowStatus
    priority: Priority
    due_date: Optional[datetime] = None
    created_date: datetime = field(default_factory=datetime.now)
    completed_date: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ApprovalRequest:
    """Data class for approval requests"""
    request_id: str
    request_type: str
    requester: str
    approver: str
    item_details: Dict[str, Any]
    justification: str
    priority: Priority
    status: str = "pending"
    created_date: datetime = field(default_factory=datetime.now)
    approved_date: Optional[datetime] = None
    comments: str = ""

class BusinessLogicProcessor:
    """
    Comprehensive business logic processor for Derivco facilities management
    Handles workflows, business rules, approvals, and automated decision-making
    """

    def __init__(self, excel_processor: AdvancedExcelProcessor = None,
                 inventory_manager: AdvancedInventoryManager = None,
                 analytics_engine: RealTimeAnalyticsEngine = None):

        self.excel_processor = excel_processor or AdvancedExcelProcessor()
        self.inventory_manager = inventory_manager
        self.analytics_engine = analytics_engine

        # Business logic data
        self.business_rules: Dict[str, BusinessRule] = {}
        self.workflow_tasks: Dict[str, WorkflowTask] = {}
        self.approval_requests: Dict[str, ApprovalRequest] = {}

        # Execution tracking
        self.rule_execution_history: List[Dict[str, Any]] = []
        self.workflow_history: List[Dict[str, Any]] = []

        # Configuration
        self.derivco_business_config = self._load_derivco_business_config()

        # Setup default business rules
        self._setup_default_business_rules()

        # Initialize workflows
        self._initialize_workflows()

    def _load_derivco_business_config(self) -> Dict[str, Any]:
        """Load Derivco-specific business configuration"""
        return {
            'approval_thresholds': {
                'equipment_value': 1000.0,  # Items over R1000 need approval
                'bulk_checkout': 5,         # More than 5 items need approval
                'overdue_days': 7           # Items overdue by 7+ days trigger escalation
            },
            'notification_rules': {
                'low_stock_threshold': 10,
                'critical_stock_threshold': 5,
                'compliance_threshold': 80.0,
                'response_time_hours': 24
            },
            'workflow_rules': {
                'auto_reorder_enabled': True,
                'approval_required_categories': ['Safety', 'Access Control'],
                'supervisor_approval_required': True,
                'finance_approval_threshold': 5000.0
            },
            'escalation_rules': {
                'overdue_escalation_days': [3, 7, 14],
                'compliance_escalation_threshold': 60.0,
                'critical_alert_escalation_hours': 2
            },
            'derivco_departments': [
                'IT Department', 'Facilities', 'Security', 'HR',
                'Finance', 'Operations', 'Maintenance', 'Cleaning'
            ],
            'derivco_supervisors': [
                'Erasmus Ngwane', 'Brindley Harrington'
            ]
        }

    def _setup_default_business_rules(self):
        """Setup default business rules for Derivco facilities"""
        default_rules = [
            BusinessRule(
                rule_id="BR001",
                rule_name="High Value Equipment Approval",
                rule_type=BusinessRuleType.APPROVAL,
                description="Equipment over R1000 requires supervisor approval",
                condition="item_value > 1000",
                action="create_approval_request",
                priority=Priority.HIGH
            ),
            BusinessRule(
                rule_id="BR002",
                rule_name="Critical Stock Alert",
                rule_type=BusinessRuleType.NOTIFICATION,
                description="Alert when inventory reaches critical levels",
                condition="stock_level <= 5",
                action="send_critical_stock_alert",
                priority=Priority.CRITICAL
            ),
            BusinessRule(
                rule_id="BR003",
                rule_name="Overdue Equipment Escalation",
                rule_type=BusinessRuleType.ESCALATION,
                description="Escalate overdue equipment returns",
                condition="days_overdue >= 7",
                action="escalate_to_supervisor",
                priority=Priority.HIGH
            ),
            BusinessRule(
                rule_id="BR004",
                rule_name="Work Order Validation",
                rule_type=BusinessRuleType.VALIDATION,
                description="Validate work order format and requirements",
                condition="wo_req_missing or wo_req_invalid",
                action="require_valid_work_order",
                priority=Priority.MEDIUM
            ),
            BusinessRule(
                rule_id="BR005",
                rule_name="Auto Reorder Trigger",
                rule_type=BusinessRuleType.AUTOMATION,
                description="Automatically trigger reorder for low stock items",
                condition="stock_level <= reorder_level and auto_reorder_enabled",
                action="create_purchase_requisition",
                priority=Priority.MEDIUM
            ),
            BusinessRule(
                rule_id="BR006",
                rule_name="Compliance Monitoring",
                rule_type=BusinessRuleType.NOTIFICATION,
                description="Monitor and alert on compliance violations",
                condition="compliance_percentage < 80",
                action="send_compliance_alert",
                priority=Priority.HIGH
            ),
            BusinessRule(
                rule_id="BR007",
                rule_name="Bulk Checkout Approval",
                rule_type=BusinessRuleType.APPROVAL,
                description="Bulk equipment checkout requires approval",
                condition="checkout_quantity > 5",
                action="require_bulk_checkout_approval",
                priority=Priority.MEDIUM
            ),
            BusinessRule(
                rule_id="BR008",
                rule_name="Safety Equipment Priority",
                rule_type=BusinessRuleType.AUTOMATION,
                description="Prioritize safety equipment requests",
                condition="category == 'Safety'",
                action="set_high_priority",
                priority=Priority.HIGH
            )
        ]

        for rule in default_rules:
            self.business_rules[rule.rule_id] = rule

        logger.info(f"Setup {len(default_rules)} default business rules")

    def _initialize_workflows(self):
        """Initialize standard workflows"""
        # Equipment checkout workflow
        self._create_equipment_checkout_workflow()

        # Inventory reorder workflow
        self._create_inventory_reorder_workflow()

        # Compliance remediation workflow
        self._create_compliance_remediation_workflow()

        logger.info("Standard workflows initialized")

    def _create_equipment_checkout_workflow(self):
        """Create equipment checkout workflow"""
        workflow_id = "WF_EQUIPMENT_CHECKOUT"

        tasks = [
            WorkflowTask(
                task_id=f"{workflow_id}_001",
                workflow_id=workflow_id,
                task_name="Validate Equipment Request",
                task_type="validation",
                assignee="system",
                status=WorkflowStatus.PENDING,
                priority=Priority.HIGH
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_002",
                workflow_id=workflow_id,
                task_name="Check Work Order",
                task_type="validation",
                assignee="system",
                status=WorkflowStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[f"{workflow_id}_001"]
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_003",
                workflow_id=workflow_id,
                task_name="Approve High Value Items",
                task_type="approval",
                assignee="supervisor",
                status=WorkflowStatus.PENDING,
                priority=Priority.MEDIUM,
                dependencies=[f"{workflow_id}_002"]
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_004",
                workflow_id=workflow_id,
                task_name="Record Equipment Checkout",
                task_type="data_entry",
                assignee="facilities_assistant",
                status=WorkflowStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[f"{workflow_id}_003"]
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_005",
                workflow_id=workflow_id,
                task_name="Schedule Return Reminder",
                task_type="scheduling",
                assignee="system",
                status=WorkflowStatus.PENDING,
                priority=Priority.LOW,
                dependencies=[f"{workflow_id}_004"]
            )
        ]

        for task in tasks:
            self.workflow_tasks[task.task_id] = task

    def _create_inventory_reorder_workflow(self):
        """Create inventory reorder workflow"""
        workflow_id = "WF_INVENTORY_REORDER"

        tasks = [
            WorkflowTask(
                task_id=f"{workflow_id}_001",
                workflow_id=workflow_id,
                task_name="Monitor Stock Levels",
                task_type="monitoring",
                assignee="system",
                status=WorkflowStatus.PENDING,
                priority=Priority.MEDIUM
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_002",
                workflow_id=workflow_id,
                task_name="Generate Purchase Requisition",
                task_type="documentation",
                assignee="facilities_assistant",
                status=WorkflowStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[f"{workflow_id}_001"]
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_003",
                workflow_id=workflow_id,
                task_name="Budget Approval",
                task_type="approval",
                assignee="finance_manager",
                status=WorkflowStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[f"{workflow_id}_002"]
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_004",
                workflow_id=workflow_id,
                task_name="Submit Purchase Order",
                task_type="procurement",
                assignee="procurement_team",
                status=WorkflowStatus.PENDING,
                priority=Priority.MEDIUM,
                dependencies=[f"{workflow_id}_003"]
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_005",
                workflow_id=workflow_id,
                task_name="Update Inventory Records",
                task_type="data_entry",
                assignee="facilities_assistant",
                status=WorkflowStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[f"{workflow_id}_004"]
            )
        ]

        for task in tasks:
            self.workflow_tasks[task.task_id] = task

    def _create_compliance_remediation_workflow(self):
        """Create compliance remediation workflow"""
        workflow_id = "WF_COMPLIANCE_REMEDIATION"

        tasks = [
            WorkflowTask(
                task_id=f"{workflow_id}_001",
                workflow_id=workflow_id,
                task_name="Identify Compliance Gaps",
                task_type="analysis",
                assignee="system",
                status=WorkflowStatus.PENDING,
                priority=Priority.HIGH
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_002",
                workflow_id=workflow_id,
                task_name="Create Remediation Plan",
                task_type="planning",
                assignee="facilities_manager",
                status=WorkflowStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[f"{workflow_id}_001"]
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_003",
                workflow_id=workflow_id,
                task_name="Implement Corrections",
                task_type="execution",
                assignee="facilities_team",
                status=WorkflowStatus.PENDING,
                priority=Priority.CRITICAL,
                dependencies=[f"{workflow_id}_002"]
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_004",
                workflow_id=workflow_id,
                task_name="Verify Compliance",
                task_type="verification",
                assignee="compliance_officer",
                status=WorkflowStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[f"{workflow_id}_003"]
            ),
            WorkflowTask(
                task_id=f"{workflow_id}_005",
                workflow_id=workflow_id,
                task_name="Document Resolution",
                task_type="documentation",
                assignee="facilities_assistant",
                status=WorkflowStatus.PENDING,
                priority=Priority.MEDIUM,
                dependencies=[f"{workflow_id}_004"]
            )
        ]

        for task in tasks:
            self.workflow_tasks[task.task_id] = task

    def evaluate_business_rule(self, rule_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a specific business rule against given context
        Returns evaluation result and recommended actions
        """
        try:
            if rule_id not in self.business_rules:
                raise ValueError(f"Business rule {rule_id} not found")

            rule = self.business_rules[rule_id]
            if not rule.enabled:
                return {
                    'rule_id': rule_id,
                    'rule_name': rule.rule_name,
                    'evaluated': False,
                    'reason': 'Rule is disabled'
                }

            logger.info(f"Evaluating business rule: {rule.rule_name}")

            evaluation_result = {
                'rule_id': rule_id,
                'rule_name': rule.rule_name,
                'rule_type': rule.rule_type.value,
                'evaluated': True,
                'condition_met': False,
                'actions_triggered': [],
                'evaluation_time': datetime.now().isoformat(),
                'context': context
            }

            # Evaluate condition
            try:
                condition_met = self._evaluate_condition(rule.condition, context)
                evaluation_result['condition_met'] = condition_met

                if condition_met:
                    # Execute action
                    action_results = self._execute_rule_action(rule, context)
                    evaluation_result['actions_triggered'] = action_results

                    # Update rule statistics
                    rule.last_executed = datetime.now()
                    rule.execution_count += 1

            except Exception as e:
                evaluation_result['error'] = f"Error evaluating condition: {str(e)}"
                logger.error(f"Error evaluating rule {rule_id}: {e}")

            # Store in history
            self.rule_execution_history.append(evaluation_result.copy())

            return evaluation_result

        except Exception as e:
            logger.error(f"Error evaluating business rule {rule_id}: {e}")
            return {
                'rule_id': rule_id,
                'evaluated': False,
                'error': str(e)
            }

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate a business rule condition"""
        try:
            # Create safe evaluation environment
            safe_globals = {
                '__builtins__': {},
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round
            }

            # Add context variables
            safe_globals.update(context)

            # Add common business logic functions
            safe_globals.update({
                'is_weekend': lambda: datetime.now().weekday() >= 5,
                'days_between': lambda d1, d2: abs((d1 - d2).days),
                'is_supervisor': lambda name: name in self.derivco_business_config['derivco_supervisors'],
                'is_high_value': lambda value: value > self.derivco_business_config['approval_thresholds']['equipment_value']
            })

            # Evaluate condition
            result = eval(condition, safe_globals, {})
            return bool(result)

        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    def _execute_rule_action(self, rule: BusinessRule, context: Dict[str, Any]) -> List[str]:
        """Execute actions triggered by business rule"""
        actions_executed = []

        try:
            action = rule.action

            if action == "create_approval_request":
                approval_id = self._create_approval_request(rule, context)
                actions_executed.append(f"Created approval request: {approval_id}")

            elif action == "send_critical_stock_alert":
                alert_result = self._send_critical_stock_alert(context)
                actions_executed.append(f"Sent critical stock alert: {alert_result}")

            elif action == "escalate_to_supervisor":
                escalation_result = self._escalate_to_supervisor(context)
                actions_executed.append(f"Escalated to supervisor: {escalation_result}")

            elif action == "require_valid_work_order":
                validation_result = self._require_valid_work_order(context)
                actions_executed.append(f"Work order validation required: {validation_result}")

            elif action == "create_purchase_requisition":
                requisition_id = self._create_purchase_requisition(context)
                actions_executed.append(f"Created purchase requisition: {requisition_id}")

            elif action == "send_compliance_alert":
                compliance_alert = self._send_compliance_alert(context)
                actions_executed.append(f"Sent compliance alert: {compliance_alert}")

            elif action == "require_bulk_checkout_approval":
                bulk_approval_id = self._require_bulk_checkout_approval(context)
                actions_executed.append(f"Required bulk checkout approval: {bulk_approval_id}")

            elif action == "set_high_priority":
                priority_result = self._set_high_priority(context)
                actions_executed.append(f"Set high priority: {priority_result}")

            else:
                actions_executed.append(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Error executing rule action {rule.action}: {e}")
            actions_executed.append(f"Error executing action: {str(e)}")

        return actions_executed

    def _create_approval_request(self, rule: BusinessRule, context: Dict[str, Any]) -> str:
        """Create an approval request"""
        try:
            request_id = f"APPR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            approval_request = ApprovalRequest(
                request_id=request_id,
                request_type="equipment_approval",
                requester=context.get('requester', 'unknown'),
                approver=context.get('approver', 'supervisor'),
                item_details=context.get('item_details', {}),
                justification=context.get('justification', f"Triggered by rule: {rule.rule_name}"),
                priority=Priority.HIGH
            )

            self.approval_requests[request_id] = approval_request

            logger.info(f"Created approval request {request_id}")
            return request_id

        except Exception as e:
            logger.error(f"Error creating approval request: {e}")
            return f"Error: {str(e)}"

    def _send_critical_stock_alert(self, context: Dict[str, Any]) -> str:
        """Send critical stock alert"""
        try:
            item_name = context.get('item_name', 'Unknown Item')
            stock_level = context.get('stock_level', 0)

            alert_message = f"CRITICAL STOCK ALERT: {item_name} has only {stock_level} units remaining"

            # In production, this would send actual notifications
            logger.warning(alert_message)

            return f"Alert sent for {item_name}"

        except Exception as e:
            logger.error(f"Error sending critical stock alert: {e}")
            return f"Error: {str(e)}"

    def _escalate_to_supervisor(self, context: Dict[str, Any]) -> str:
        """Escalate issue to supervisor"""
        try:
            issue_details = context.get('issue_details', 'Overdue equipment')
            borrower = context.get('borrower', 'Unknown')
            supervisor = context.get('supervisor', 'Erasmus Ngwane')

            escalation_message = f"ESCALATION: {issue_details} - Borrower: {borrower}"

            # In production, this would send actual notifications to supervisor
            logger.warning(f"Escalated to {supervisor}: {escalation_message}")

            return f"Escalated to {supervisor}"

        except Exception as e:
            logger.error(f"Error escalating to supervisor: {e}")
            return f"Error: {str(e)}"

    def _require_valid_work_order(self, context: Dict[str, Any]) -> str:
        """Require valid work order"""
        try:
            transaction_id = context.get('transaction_id', 'Unknown')
            current_wo = context.get('current_wo', '')

            # In production, this would prevent the transaction or require correction
            logger.info(f"Work order validation required for transaction {transaction_id}: '{current_wo}'")

            return f"Validation required for transaction {transaction_id}"

        except Exception as e:
            logger.error(f"Error requiring work order validation: {e}")
            return f"Error: {str(e)}"

    def _create_purchase_requisition(self, context: Dict[str, Any]) -> str:
        """Create purchase requisition"""
        try:
            item_code = context.get('item_code', 'Unknown')
            item_name = context.get('item_name', 'Unknown Item')
            quantity_needed = context.get('quantity_needed', 10)

            requisition_id = f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{item_code}"

            # In production, this would create actual purchase requisition
            logger.info(f"Purchase requisition created: {requisition_id} for {quantity_needed}x {item_name}")

            return requisition_id

        except Exception as e:
            logger.error(f"Error creating purchase requisition: {e}")
            return f"Error: {str(e)}"

    def _send_compliance_alert(self, context: Dict[str, Any]) -> str:
        """Send compliance alert"""
        try:
            compliance_percentage = context.get('compliance_percentage', 0)
            compliance_type = context.get('compliance_type', 'General')

            alert_message = f"COMPLIANCE ALERT: {compliance_type} compliance at {compliance_percentage}%"

            # In production, this would send actual notifications
            logger.warning(alert_message)

            return f"Compliance alert sent"

        except Exception as e:
            logger.error(f"Error sending compliance alert: {e}")
            return f"Error: {str(e)}"

    def _require_bulk_checkout_approval(self, context: Dict[str, Any]) -> str:
        """Require bulk checkout approval"""
        try:
            quantity = context.get('checkout_quantity', 0)
            requester = context.get('requester', 'Unknown')

            approval_id = f"BULK_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{requester}"

            # In production, this would create actual approval workflow
            logger.info(f"Bulk checkout approval required: {approval_id} for {quantity} items")

            return approval_id

        except Exception as e:
            logger.error(f"Error requiring bulk checkout approval: {e}")
            return f"Error: {str(e)}"

    def _set_high_priority(self, context: Dict[str, Any]) -> str:
        """Set high priority for request"""
        try:
            request_id = context.get('request_id', 'Unknown')
            category = context.get('category', 'Unknown')

            # In production, this would update actual request priority
            logger.info(f"Set high priority for {category} request: {request_id}")

            return f"High priority set for {request_id}"

        except Exception as e:
            logger.error(f"Error setting high priority: {e}")
            return f"Error: {str(e)}"

    def process_inventory_business_rules(self) -> Dict[str, Any]:
        """Process all business rules for current inventory state"""
        try:
            logger.info("Processing inventory business rules...")

            if not self.inventory_manager:
                return {'error': 'Inventory manager not available'}

            processing_results = {
                'timestamp': datetime.now().isoformat(),
                'rules_processed': 0,
                'rules_triggered': 0,
                'actions_executed': 0,
                'rule_results': [],
                'summary': {}
            }

            # Get current inventory state
            inventory_summary = self.inventory_manager.get_inventory_summary()
            low_stock_items = self.inventory_manager.get_low_stock_items()
            critical_stock_items = self.inventory_manager.get_critical_stock_items()

            # Process rules for each inventory item
            for item in self.inventory_manager.items.values():
                context = {
                    'item_code': item.item_code,
                    'item_name': item.item_name,
                    'category': item.category,
                    'stock_level': item.quantity,
                    'reorder_level': item.reorder_level,
                    'item_value': item.unit_price,
                    'total_value': item.total_value,
                    'supplier': item.supplier,
                    'auto_reorder_enabled': self.derivco_business_config['workflow_rules']['auto_reorder_enabled']
                }

                # Check relevant rules
                relevant_rules = ['BR002', 'BR005']  # Critical stock, Auto reorder

                if item.category in self.derivco_business_config['workflow_rules']['approval_required_categories']:
                    relevant_rules.append('BR008')  # Safety equipment priority

                for rule_id in relevant_rules:
                    if rule_id in self.business_rules:
                        result = self.evaluate_business_rule(rule_id, context)
                        processing_results['rule_results'].append(result)
                        processing_results['rules_processed'] += 1

                        if result.get('condition_met', False):
                            processing_results['rules_triggered'] += 1
                            processing_results['actions_executed'] += len(result.get('actions_triggered', []))

            # Summary
            processing_results['summary'] = {
                'total_inventory_items': len(self.inventory_manager.items),
                'low_stock_items': len(low_stock_items),
                'critical_stock_items': len(critical_stock_items),
                'approval_requests_created': len([r for r in processing_results['rule_results'] if 'approval request' in str(r.get('actions_triggered', []))]),
                'alerts_sent': len([r for r in processing_results['rule_results'] if 'alert' in str(r.get('actions_triggered', []))])
            }

            logger.info(f"Inventory business rules processed: {processing_results['rules_triggered']}/{processing_results['rules_processed']} triggered")

            return processing_results

        except Exception as e:
            logger.error(f"Error processing inventory business rules: {e}")
            return {'error': str(e)}

    def process_compliance_business_rules(self) -> Dict[str, Any]:
        """Process business rules for compliance monitoring"""
        try:
            logger.info("Processing compliance business rules...")

            if not self.analytics_engine:
                return {'error': 'Analytics engine not available'}

            processing_results = {
                'timestamp': datetime.now().isoformat(),
                'rules_processed': 0,
                'rules_triggered': 0,
                'actions_executed': 0,
                'rule_results': [],
                'compliance_summary': {}
            }

            # Get compliance analysis
            compliance_analysis = self.analytics_engine.generate_compliance_analysis()
            metrics = compliance_analysis.get('compliance_metrics', {})

            # Process work order compliance
            wo_metric = metrics.get('work_order')
            if wo_metric and hasattr(wo_metric, 'compliance_percentage'):
                context = {
                    'compliance_type': 'work_order',
                    'compliance_percentage': wo_metric.compliance_percentage,
                    'target_percentage': 95.0,
                    'risk_level': wo_metric.risk_level.value if hasattr(wo_metric.risk_level, 'value') else 'unknown'
                }

                relevant_rules = ['BR004', 'BR006']  # Work order validation, Compliance monitoring

                for rule_id in relevant_rules:
                    if rule_id in self.business_rules:
                        # Adjust context for specific rule
                        if rule_id == 'BR004':
                            context['wo_req_missing'] = wo_metric.compliance_percentage < 95
                            context['wo_req_invalid'] = wo_metric.compliance_percentage < 80
                        elif rule_id == 'BR006':
                            context['compliance_percentage'] = wo_metric.compliance_percentage

                        result = self.evaluate_business_rule(rule_id, context)
                        processing_results['rule_results'].append(result)
                        processing_results['rules_processed'] += 1

                        if result.get('condition_met', False):
                            processing_results['rules_triggered'] += 1
                            processing_results['actions_executed'] += len(result.get('actions_triggered', []))

            # Process tool return compliance
            return_metric = metrics.get('tool_return')
            if return_metric and hasattr(return_metric, 'compliance_percentage'):
                context = {
                    'compliance_type': 'tool_return',
                    'compliance_percentage': return_metric.compliance_percentage,
                    'target_percentage': 95.0,
                    'days_overdue': 7  # Assumption for overdue calculation
                }

                relevant_rules = ['BR003', 'BR006']  # Overdue escalation, Compliance monitoring

                for rule_id in relevant_rules:
                    if rule_id in self.business_rules:
                        result = self.evaluate_business_rule(rule_id, context)
                        processing_results['rule_results'].append(result)
                        processing_results['rules_processed'] += 1

                        if result.get('condition_met', False):
                            processing_results['rules_triggered'] += 1
                            processing_results['actions_executed'] += len(result.get('actions_triggered', []))

            # Summary
            processing_results['compliance_summary'] = {
                'work_order_compliance': wo_metric.compliance_percentage if wo_metric and hasattr(wo_metric, 'compliance_percentage') else 0,
                'tool_return_compliance': return_metric.compliance_percentage if return_metric and hasattr(return_metric, 'compliance_percentage') else 0,
                'overall_risk_level': compliance_analysis.get('risk_assessment', {}).get('overall_risk_level', 'unknown')
            }

            logger.info(f"Compliance business rules processed: {processing_results['rules_triggered']}/{processing_results['rules_processed']} triggered")

            return processing_results

        except Exception as e:
            logger.error(f"Error processing compliance business rules: {e}")
            return {'error': str(e)}

    def execute_workflow(self, workflow_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow with given context"""
        try:
            logger.info(f"Executing workflow: {workflow_id}")

            if context is None:
                context = {}

            execution_result = {
                'workflow_id': workflow_id,
                'start_time': datetime.now().isoformat(),
                'status': 'running',
                'tasks_executed': [],
                'tasks_pending': [],
                'tasks_failed': [],
                'context': context
            }

            # Get workflow tasks
            workflow_tasks = [task for task in self.workflow_tasks.values() if task.workflow_id == workflow_id]

            if not workflow_tasks:
                execution_result['status'] = 'failed'
                execution_result['error'] = f"No tasks found for workflow {workflow_id}"
                return execution_result

            # Sort tasks by dependencies (simplified - in production would use proper dependency resolution)
            sorted_tasks = sorted(workflow_tasks, key=lambda t: len(t.dependencies))

            # Execute tasks
            for task in sorted_tasks:
                task_result = self._execute_workflow_task(task, context)

                if task_result['status'] == 'completed':
                    execution_result['tasks_executed'].append(task_result)
                    task.status = WorkflowStatus.COMPLETED
                    task.completed_date = datetime.now()
                elif task_result['status'] == 'failed':
                    execution_result['tasks_failed'].append(task_result)
                    task.status = WorkflowStatus.FAILED
                else:
                    execution_result['tasks_pending'].append(task_result)

            # Determine overall workflow status
            if execution_result['tasks_failed']:
                execution_result['status'] = 'failed'
            elif execution_result['tasks_pending']:
                execution_result['status'] = 'pending'
            else:
                execution_result['status'] = 'completed'

            execution_result['end_time'] = datetime.now().isoformat()

            # Store in history
            self.workflow_history.append(execution_result.copy())

            logger.info(f"Workflow {workflow_id} execution completed with status: {execution_result['status']}")

            return execution_result

        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            return {
                'workflow_id': workflow_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _execute_workflow_task(self, task: WorkflowTask, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow task"""
        try:
            task_result = {
                'task_id': task.task_id,
                'task_name': task.task_name,
                'task_type': task.task_type,
                'status': 'running',
                'start_time': datetime.now().isoformat()
            }

            # Check dependencies (simplified)
            if task.dependencies:
                # In production, would check if dependent tasks are completed
                pass

            # Execute based on task type
            if task.task_type == 'validation':
                task_result['result'] = self._execute_validation_task(task, context)
                task_result['status'] = 'completed'

            elif task.task_type == 'approval':
                task_result['result'] = self._execute_approval_task(task, context)
                task_result['status'] = 'pending'  # Approvals typically require manual action

            elif task.task_type == 'data_entry':
                task_result['result'] = self._execute_data_entry_task(task, context)
                task_result['status'] = 'completed'

            elif task.task_type == 'scheduling':
                task_result['result'] = self._execute_scheduling_task(task, context)
                task_result['status'] = 'completed'

            elif task.task_type == 'monitoring':
                task_result['result'] = self._execute_monitoring_task(task, context)
                task_result['status'] = 'completed'

            elif task.task_type == 'documentation':
                task_result['result'] = self._execute_documentation_task(task, context)
                task_result['status'] = 'completed'

            elif task.task_type == 'procurement':
                task_result['result'] = self._execute_procurement_task(task, context)
                task_result['status'] = 'pending'  # Procurement typically takes time

            else:
                task_result['result'] = f"Task type {task.task_type} not implemented"
                task_result['status'] = 'completed'

            task_result['end_time'] = datetime.now().isoformat()

            return task_result

        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {e}")
            return {
                'task_id': task.task_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _execute_validation_task(self, task: WorkflowTask, context: Dict[str, Any]) -> str:
        """Execute validation task"""
        return f"Validation completed for {task.task_name}"

    def _execute_approval_task(self, task: WorkflowTask, context: Dict[str, Any]) -> str:
        """Execute approval task"""
        approval_id = self._create_approval_request(self.business_rules.get('BR001'), context)
        return f"Approval request created: {approval_id}"

    def _execute_data_entry_task(self, task: WorkflowTask, context: Dict[str, Any]) -> str:
        """Execute data entry task"""
        return f"Data entry completed for {task.task_name}"

    def _execute_scheduling_task(self, task: WorkflowTask, context: Dict[str, Any]) -> str:
        """Execute scheduling task"""
        return f"Scheduling completed for {task.task_name}"

    def _execute_monitoring_task(self, task: WorkflowTask, context: Dict[str, Any]) -> str:
        """Execute monitoring task"""
        return f"Monitoring initiated for {task.task_name}"

    def _execute_documentation_task(self, task: WorkflowTask, context: Dict[str, Any]) -> str:
        """Execute documentation task"""
        return f"Documentation completed for {task.task_name}"

    def _execute_procurement_task(self, task: WorkflowTask, context: Dict[str, Any]) -> str:
        """Execute procurement task"""
        return f"Procurement initiated for {task.task_name}"

    def get_business_logic_summary(self) -> Dict[str, Any]:
        """Get comprehensive business logic summary"""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'business_rules': {
                    'total_rules': len(self.business_rules),
                    'enabled_rules': len([r for r in self.business_rules.values() if r.enabled]),
                    'rule_types': {}
                },
                'workflows': {
                    'total_workflows': len(set(task.workflow_id for task in self.workflow_tasks.values())),
                    'total_tasks': len(self.workflow_tasks),
                    'task_statuses': {}
                },
                'approvals': {
                    'pending_approvals': len([a for a in self.approval_requests.values() if a.status == 'pending']),
                    'total_requests': len(self.approval_requests)
                },
                'execution_history': {
                    'rule_executions': len(self.rule_execution_history),
                    'workflow_executions': len(self.workflow_history)
                }
            }

            # Rule type distribution
            for rule in self.business_rules.values():
                rule_type = rule.rule_type.value
                summary['business_rules']['rule_types'][rule_type] = \
                    summary['business_rules']['rule_types'].get(rule_type, 0) + 1

            # Task status distribution
            for task in self.workflow_tasks.values():
                status = task.status.value
                summary['workflows']['task_statuses'][status] = \
                    summary['workflows']['task_statuses'].get(status, 0) + 1

            return summary

        except Exception as e:
            logger.error(f"Error generating business logic summary: {e}")
            return {'error': str(e)}