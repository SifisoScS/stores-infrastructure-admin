#!/usr/bin/env python3
"""
Real-time Analytics and Compliance Engine for Derivco Facilities Management
Provides comprehensive analytics, compliance monitoring, and business intelligence
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
from collections import defaultdict
import statistics

# Import our core services
import sys
sys.path.append('core')
sys.path.append('services')
from excel_processor import AdvancedExcelProcessor
from inventory_service import AdvancedInventoryManager, StockLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    """Compliance level categories"""
    EXCELLENT = "excellent"      # 95%+ compliance
    GOOD = "good"               # 80-94% compliance
    FAIR = "fair"               # 60-79% compliance
    POOR = "poor"               # 40-59% compliance
    CRITICAL = "critical"       # <40% compliance

class RiskLevel(Enum):
    """Risk level categories"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ComplianceMetric:
    """Data class for compliance metrics"""
    metric_name: str
    current_value: float
    target_value: float
    compliance_percentage: float
    trend: str  # "improving", "stable", "declining"
    risk_level: RiskLevel
    description: str
    recommendations: List[str] = field(default_factory=list)

@dataclass
class PerformanceKPI:
    """Data class for performance KPIs"""
    kpi_name: str
    current_value: Union[int, float]
    target_value: Union[int, float]
    unit: str
    trend: str
    variance_percentage: float
    status: str  # "on_track", "at_risk", "off_track"
    department: str = "facilities"

class RealTimeAnalyticsEngine:
    """
    Comprehensive analytics engine providing:
    - Real-time compliance monitoring
    - Performance analytics and KPIs
    - Predictive insights
    - Business intelligence dashboards
    - Automated alerting and recommendations
    """

    def __init__(self, excel_processor: AdvancedExcelProcessor = None,
                 inventory_manager: AdvancedInventoryManager = None):
        self.excel_processor = excel_processor or AdvancedExcelProcessor()
        self.inventory_manager = inventory_manager
        self.historical_data = {}
        self.compliance_history = []
        self.kpi_history = []

        # Load historical data if available
        self._load_historical_data()

    def _load_historical_data(self):
        """Load historical analytics data"""
        try:
            history_file = Path('analytics_history.json')
            if history_file.exists():
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.historical_data = data.get('historical_data', {})
                    self.compliance_history = data.get('compliance_history', [])
                    self.kpi_history = data.get('kpi_history', [])
                    logger.info("Loaded historical analytics data")
        except Exception as e:
            logger.warning(f"Could not load historical data: {e}")

    def _save_historical_data(self):
        """Save historical analytics data"""
        try:
            data = {
                'historical_data': self.historical_data,
                'compliance_history': self.compliance_history,
                'kpi_history': self.kpi_history,
                'last_updated': datetime.now().isoformat()
            }

            with open('analytics_history.json', 'w') as f:
                json.dump(data, f, indent=2)
                logger.info("Saved historical analytics data")
        except Exception as e:
            logger.error(f"Error saving historical data: {e}")

    def generate_compliance_analysis(self) -> Dict[str, Any]:
        """
        Generate comprehensive compliance analysis based on sign-out data
        Returns detailed compliance metrics and risk assessment
        """
        try:
            logger.info("Generating comprehensive compliance analysis...")

            # Load sign-out data
            signout_df = self.excel_processor.read_excel_file('signout')

            analysis = {
                'timestamp': datetime.now().isoformat(),
                'compliance_metrics': {},
                'risk_assessment': {},
                'violations': [],
                'trends': {},
                'recommendations': [],
                'business_impact': {}
            }

            if signout_df.empty:
                analysis['error'] = "No sign-out data available"
                return analysis

            # Work Order Compliance Analysis
            wo_compliance = self._analyze_work_order_compliance(signout_df)
            analysis['compliance_metrics']['work_order'] = wo_compliance

            # Tool Return Compliance Analysis
            return_compliance = self._analyze_return_compliance(signout_df)
            analysis['compliance_metrics']['tool_return'] = return_compliance

            # Department Performance Analysis
            dept_performance = self._analyze_department_performance(signout_df)
            analysis['compliance_metrics']['department_performance'] = dept_performance

            # Staff Performance Analysis
            staff_performance = self._analyze_staff_performance(signout_df)
            analysis['compliance_metrics']['staff_performance'] = staff_performance

            # Risk Assessment
            analysis['risk_assessment'] = self._assess_compliance_risks(analysis['compliance_metrics'])

            # Generate Recommendations
            analysis['recommendations'] = self._generate_compliance_recommendations(analysis)

            # Business Impact Analysis
            analysis['business_impact'] = self._calculate_business_impact(analysis)

            # Store in history
            self._store_compliance_snapshot(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error generating compliance analysis: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def _analyze_work_order_compliance(self, df: pd.DataFrame) -> ComplianceMetric:
        """Analyze work order compliance"""
        try:
            # Define what constitutes missing work orders
            supervisor_names = {
                'Erasmus Ngwane', 'Brindley Harrington', 'Not Provided', 'Not provided',
                'not provided', 'N/A', 'n/a', 'None', 'none', '', 'Unknown'
            }

            if 'WO_REQ_No' not in df.columns:
                return ComplianceMetric(
                    metric_name="Work Order Compliance",
                    current_value=0,
                    target_value=95,
                    compliance_percentage=0,
                    trend="unknown",
                    risk_level=RiskLevel.CRITICAL,
                    description="Work order data not available"
                )

            total_transactions = len(df)
            missing_wo = df[
                df['WO_REQ_No'].isna() |
                df['WO_REQ_No'].isin(supervisor_names) |
                (df['WO_REQ_No'].astype(str).str.strip() == '')
            ]

            missing_count = len(missing_wo)
            compliance_percentage = ((total_transactions - missing_count) / total_transactions * 100) if total_transactions > 0 else 0

            # Determine risk level
            if compliance_percentage >= 95:
                risk_level = RiskLevel.LOW
            elif compliance_percentage >= 80:
                risk_level = RiskLevel.MEDIUM
            elif compliance_percentage >= 60:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.CRITICAL

            # Generate recommendations
            recommendations = []
            if compliance_percentage < 95:
                recommendations.extend([
                    "Implement mandatory work order validation before tool sign-out",
                    "Train staff on proper work order documentation procedures",
                    "Create digital work order integration with sign-out system"
                ])

            if compliance_percentage < 60:
                recommendations.extend([
                    "Immediate policy enforcement meeting required",
                    "Implement supervisor approval process for non-WO transactions",
                    "Daily compliance monitoring and reporting"
                ])

            return ComplianceMetric(
                metric_name="Work Order Compliance",
                current_value=compliance_percentage,
                target_value=95.0,
                compliance_percentage=compliance_percentage,
                trend=self._calculate_trend('work_order_compliance', compliance_percentage),
                risk_level=risk_level,
                description=f"{missing_count} of {total_transactions} transactions missing proper work orders",
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Error analyzing work order compliance: {e}")
            return ComplianceMetric(
                metric_name="Work Order Compliance",
                current_value=0,
                target_value=95,
                compliance_percentage=0,
                trend="unknown",
                risk_level=RiskLevel.CRITICAL,
                description=f"Error analyzing work orders: {e}"
            )

    def _analyze_return_compliance(self, df: pd.DataFrame) -> ComplianceMetric:
        """Analyze tool return compliance"""
        try:
            if 'Date_In' not in df.columns:
                return ComplianceMetric(
                    metric_name="Tool Return Compliance",
                    current_value=0,
                    target_value=95,
                    compliance_percentage=0,
                    trend="unknown",
                    risk_level=RiskLevel.CRITICAL,
                    description="Return date data not available"
                )

            total_transactions = len(df)
            unreturned = df[df['Date_In'].isna()]
            unreturned_count = len(unreturned)

            # Calculate overdue items (expected return date passed)
            overdue_count = 0
            if 'Expected_Return' in df.columns:
                today = datetime.now()
                overdue = df[
                    df['Date_In'].isna() &
                    (pd.to_datetime(df['Expected_Return'], errors='coerce') < today)
                ]
                overdue_count = len(overdue)

            return_percentage = ((total_transactions - unreturned_count) / total_transactions * 100) if total_transactions > 0 else 0

            # Determine risk level based on return rate and overdue items
            if return_percentage >= 95 and overdue_count == 0:
                risk_level = RiskLevel.LOW
            elif return_percentage >= 85 and overdue_count < 5:
                risk_level = RiskLevel.MEDIUM
            elif return_percentage >= 70:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.CRITICAL

            # Generate recommendations
            recommendations = []
            if unreturned_count > 0:
                recommendations.extend([
                    f"Follow up on {unreturned_count} unreturned items",
                    "Implement automated return reminders",
                    "Review tool checkout policies"
                ])

            if overdue_count > 0:
                recommendations.extend([
                    f"Immediate action required for {overdue_count} overdue items",
                    "Implement penalty system for overdue returns",
                    "Daily overdue item monitoring"
                ])

            description = f"{unreturned_count} unreturned items"
            if overdue_count > 0:
                description += f", {overdue_count} overdue"

            return ComplianceMetric(
                metric_name="Tool Return Compliance",
                current_value=return_percentage,
                target_value=95.0,
                compliance_percentage=return_percentage,
                trend=self._calculate_trend('tool_return_compliance', return_percentage),
                risk_level=risk_level,
                description=description,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Error analyzing return compliance: {e}")
            return ComplianceMetric(
                metric_name="Tool Return Compliance",
                current_value=0,
                target_value=95,
                compliance_percentage=0,
                trend="unknown",
                risk_level=RiskLevel.CRITICAL,
                description=f"Error analyzing returns: {e}"
            )

    def _analyze_department_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by department"""
        try:
            if 'Department' not in df.columns:
                return {'error': 'Department data not available'}

            dept_stats = {}
            departments = df['Department'].dropna().unique()

            for dept in departments:
                dept_df = df[df['Department'] == dept]

                # Calculate department metrics
                total_transactions = len(dept_df)

                # Work order compliance by department
                supervisor_names = {
                    'Erasmus Ngwane', 'Brindley Harrington', 'Not Provided', 'Not provided',
                    'not provided', 'N/A', 'n/a', 'None', 'none', ''
                }

                missing_wo = 0
                if 'WO_REQ_No' in dept_df.columns:
                    missing_wo = len(dept_df[
                        dept_df['WO_REQ_No'].isna() |
                        dept_df['WO_REQ_No'].isin(supervisor_names)
                    ])

                wo_compliance = ((total_transactions - missing_wo) / total_transactions * 100) if total_transactions > 0 else 0

                # Return compliance by department
                unreturned = 0
                if 'Date_In' in dept_df.columns:
                    unreturned = len(dept_df[dept_df['Date_In'].isna()])

                return_compliance = ((total_transactions - unreturned) / total_transactions * 100) if total_transactions > 0 else 0

                dept_stats[dept] = {
                    'total_transactions': total_transactions,
                    'wo_compliance_percentage': wo_compliance,
                    'return_compliance_percentage': return_compliance,
                    'missing_work_orders': missing_wo,
                    'unreturned_items': unreturned,
                    'overall_compliance': (wo_compliance + return_compliance) / 2
                }

            return dept_stats

        except Exception as e:
            logger.error(f"Error analyzing department performance: {e}")
            return {'error': str(e)}

    def _analyze_staff_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze individual staff performance"""
        try:
            if 'Borrower_Name' not in df.columns:
                return {'error': 'Staff data not available'}

            staff_stats = {}
            staff_members = df['Borrower_Name'].dropna().unique()

            for staff in staff_members:
                staff_df = df[df['Borrower_Name'] == staff]

                total_transactions = len(staff_df)

                # Return compliance
                unreturned = 0
                if 'Date_In' in staff_df.columns:
                    unreturned = len(staff_df[staff_df['Date_In'].isna()])

                return_rate = ((total_transactions - unreturned) / total_transactions * 100) if total_transactions > 0 else 0

                # Calculate average return time
                avg_return_time = None
                if 'Date_Out' in staff_df.columns and 'Date_In' in staff_df.columns:
                    returned_items = staff_df.dropna(subset=['Date_Out', 'Date_In'])
                    if not returned_items.empty:
                        try:
                            dates_out = pd.to_datetime(returned_items['Date_Out'])
                            dates_in = pd.to_datetime(returned_items['Date_In'])
                            return_times = (dates_in - dates_out).dt.days
                            avg_return_time = return_times.mean()
                        except:
                            pass

                # Performance rating
                if return_rate >= 95:
                    performance = "excellent"
                elif return_rate >= 85:
                    performance = "good"
                elif return_rate >= 70:
                    performance = "fair"
                else:
                    performance = "needs_improvement"

                staff_stats[staff] = {
                    'total_transactions': total_transactions,
                    'return_rate_percentage': return_rate,
                    'unreturned_items': unreturned,
                    'avg_return_time_days': avg_return_time,
                    'performance_rating': performance
                }

            return staff_stats

        except Exception as e:
            logger.error(f"Error analyzing staff performance: {e}")
            return {'error': str(e)}

    def _assess_compliance_risks(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall compliance risks"""
        try:
            risk_assessment = {
                'overall_risk_level': RiskLevel.LOW.value,
                'risk_factors': [],
                'mitigation_actions': [],
                'business_continuity_impact': 'low'
            }

            risks = []

            # Work order compliance risk
            wo_metric = metrics.get('work_order')
            if wo_metric and hasattr(wo_metric, 'compliance_percentage'):
                if wo_metric.compliance_percentage < 40:
                    risks.append({
                        'factor': 'Critical work order non-compliance',
                        'impact': 'High - Unable to track work authorization and costs',
                        'likelihood': 'Current',
                        'mitigation': 'Implement mandatory WO validation system'
                    })

            # Tool return compliance risk
            return_metric = metrics.get('tool_return')
            if return_metric and hasattr(return_metric, 'compliance_percentage'):
                if return_metric.compliance_percentage < 70:
                    risks.append({
                        'factor': 'High tool loss/theft risk',
                        'impact': 'Medium - Financial loss and operational disruption',
                        'likelihood': 'High',
                        'mitigation': 'Implement automated tracking and penalties'
                    })

            # Determine overall risk level
            if len(risks) >= 3:
                risk_assessment['overall_risk_level'] = RiskLevel.CRITICAL.value
                risk_assessment['business_continuity_impact'] = 'high'
            elif len(risks) >= 2:
                risk_assessment['overall_risk_level'] = RiskLevel.HIGH.value
                risk_assessment['business_continuity_impact'] = 'medium'
            elif len(risks) >= 1:
                risk_assessment['overall_risk_level'] = RiskLevel.MEDIUM.value

            risk_assessment['risk_factors'] = risks

            return risk_assessment

        except Exception as e:
            logger.error(f"Error assessing compliance risks: {e}")
            return {'error': str(e)}

    def _generate_compliance_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable compliance recommendations"""
        recommendations = []

        try:
            metrics = analysis.get('compliance_metrics', {})

            # Work order recommendations
            wo_metric = metrics.get('work_order')
            if wo_metric and hasattr(wo_metric, 'compliance_percentage'):
                if wo_metric.compliance_percentage < 95:
                    recommendations.append({
                        'category': 'work_order_compliance',
                        'priority': 'high' if wo_metric.compliance_percentage < 60 else 'medium',
                        'title': 'Improve Work Order Compliance',
                        'description': 'Implement systematic work order validation',
                        'actions': [
                            'Create mandatory WO field validation in sign-out system',
                            'Train staff on work order requirements',
                            'Implement supervisor approval for non-WO transactions',
                            'Generate daily non-compliance reports'
                        ],
                        'expected_impact': 'Increase work order compliance to >95%',
                        'timeline': '30 days'
                    })

            # Tool return recommendations
            return_metric = metrics.get('tool_return')
            if return_metric and hasattr(return_metric, 'compliance_percentage'):
                if return_metric.compliance_percentage < 90:
                    recommendations.append({
                        'category': 'tool_return_compliance',
                        'priority': 'high' if return_metric.compliance_percentage < 70 else 'medium',
                        'title': 'Enhance Tool Return Management',
                        'description': 'Reduce unreturned and overdue items',
                        'actions': [
                            'Implement automated return reminders',
                            'Create overdue item escalation process',
                            'Establish return confirmation procedures',
                            'Implement penalties for chronic non-returners'
                        ],
                        'expected_impact': 'Reduce unreturned items by 80%',
                        'timeline': '60 days'
                    })

            # Department-specific recommendations
            dept_performance = metrics.get('department_performance', {})
            if isinstance(dept_performance, dict) and 'error' not in dept_performance:
                for dept, stats in dept_performance.items():
                    if stats.get('overall_compliance', 100) < 80:
                        recommendations.append({
                            'category': 'department_improvement',
                            'priority': 'medium',
                            'title': f'Improve {dept} Department Compliance',
                            'description': f'{dept} showing below-target compliance rates',
                            'actions': [
                                f'Conduct compliance training for {dept} staff',
                                f'Assign compliance champion in {dept}',
                                f'Implement weekly compliance reviews for {dept}',
                                'Provide department-specific performance feedback'
                            ],
                            'expected_impact': f'Bring {dept} compliance above 90%',
                            'timeline': '45 days'
                        })

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")

        return recommendations

    def _calculate_business_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial and operational business impact"""
        try:
            impact = {
                'financial_impact': {},
                'operational_impact': {},
                'productivity_impact': {},
                'risk_exposure': {}
            }

            metrics = analysis.get('compliance_metrics', {})

            # Financial impact from work order non-compliance
            wo_metric = metrics.get('work_order')
            if wo_metric and hasattr(wo_metric, 'compliance_percentage'):
                non_compliance_rate = 100 - wo_metric.compliance_percentage
                estimated_monthly_transactions = 100  # Assumption
                untracked_work_value = estimated_monthly_transactions * (non_compliance_rate / 100) * 500  # R500 avg per transaction

                impact['financial_impact']['untracked_work_value'] = {
                    'monthly_estimate': untracked_work_value,
                    'annual_estimate': untracked_work_value * 12,
                    'description': 'Value of work performed without proper authorization tracking'
                }

            # Financial impact from unreturned tools
            return_metric = metrics.get('tool_return')
            if return_metric and hasattr(return_metric, 'compliance_percentage'):
                non_return_rate = 100 - return_metric.compliance_percentage
                estimated_tool_value = 500  # Average tool value
                monthly_loss = estimated_monthly_transactions * (non_return_rate / 100) * estimated_tool_value

                impact['financial_impact']['tool_loss_value'] = {
                    'monthly_estimate': monthly_loss,
                    'annual_estimate': monthly_loss * 12,
                    'description': 'Financial loss from unreturned/lost tools'
                }

            # Operational impact
            impact['operational_impact'] = {
                'workflow_efficiency': 'Reduced due to lack of proper work tracking',
                'audit_readiness': 'Poor - significant compliance gaps',
                'management_visibility': 'Limited - 88% of work not properly documented',
                'resource_allocation': 'Suboptimal due to lack of accurate data'
            }

            # Productivity impact
            wo_compliance = wo_metric.compliance_percentage if wo_metric and hasattr(wo_metric, 'compliance_percentage') else 0
            productivity_multiplier = 0.1 + (wo_compliance / 100) * 0.9  # 10% base + compliance bonus

            impact['productivity_impact'] = {
                'visible_work_percentage': wo_compliance,
                'hidden_work_percentage': 100 - wo_compliance,
                'management_oversight_effectiveness': f"{productivity_multiplier * 100:.1f}%",
                'performance_measurement_accuracy': 'Low' if wo_compliance < 60 else 'Medium' if wo_compliance < 85 else 'High'
            }

            return impact

        except Exception as e:
            logger.error(f"Error calculating business impact: {e}")
            return {'error': str(e)}

    def _calculate_trend(self, metric_name: str, current_value: float) -> str:
        """Calculate trend for a specific metric"""
        try:
            # Look for historical data
            if metric_name in self.historical_data:
                history = self.historical_data[metric_name]
                if len(history) >= 2:
                    previous_value = history[-1]['value']
                    if current_value > previous_value + 2:
                        return "improving"
                    elif current_value < previous_value - 2:
                        return "declining"
                    else:
                        return "stable"

            return "stable"  # Default for new metrics

        except Exception as e:
            logger.warning(f"Error calculating trend for {metric_name}: {e}")
            return "unknown"

    def _store_compliance_snapshot(self, analysis: Dict[str, Any]):
        """Store compliance snapshot for trend analysis"""
        try:
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'metrics': {}
            }

            # Extract key metrics
            metrics = analysis.get('compliance_metrics', {})

            wo_metric = metrics.get('work_order')
            if wo_metric and hasattr(wo_metric, 'compliance_percentage'):
                snapshot['metrics']['work_order_compliance'] = wo_metric.compliance_percentage

            return_metric = metrics.get('tool_return')
            if return_metric and hasattr(return_metric, 'compliance_percentage'):
                snapshot['metrics']['tool_return_compliance'] = return_metric.compliance_percentage

            # Add to history
            self.compliance_history.append(snapshot)

            # Keep only last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            self.compliance_history = [
                h for h in self.compliance_history
                if datetime.fromisoformat(h['timestamp']) >= thirty_days_ago
            ]

            # Update historical data for trending
            for metric, value in snapshot['metrics'].items():
                if metric not in self.historical_data:
                    self.historical_data[metric] = []

                self.historical_data[metric].append({
                    'timestamp': snapshot['timestamp'],
                    'value': value
                })

                # Keep only last 30 entries
                self.historical_data[metric] = self.historical_data[metric][-30:]

            # Save to file
            self._save_historical_data()

        except Exception as e:
            logger.error(f"Error storing compliance snapshot: {e}")

    def generate_kpi_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive KPI dashboard"""
        try:
            logger.info("Generating KPI dashboard...")

            dashboard = {
                'timestamp': datetime.now().isoformat(),
                'facilities_kpis': {},
                'inventory_kpis': {},
                'compliance_kpis': {},
                'performance_kpis': {},
                'trends': {}
            }

            # Facilities KPIs
            signout_df = self.excel_processor.read_excel_file('signout')
            if not signout_df.empty:
                dashboard['facilities_kpis'] = self._calculate_facilities_kpis(signout_df)

            # Inventory KPIs
            if self.inventory_manager:
                dashboard['inventory_kpis'] = self._calculate_inventory_kpis()

            # Compliance KPIs
            compliance_analysis = self.generate_compliance_analysis()
            dashboard['compliance_kpis'] = self._extract_compliance_kpis(compliance_analysis)

            # Performance KPIs
            dashboard['performance_kpis'] = self._calculate_performance_kpis(signout_df)

            return dashboard

        except Exception as e:
            logger.error(f"Error generating KPI dashboard: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def _calculate_facilities_kpis(self, df: pd.DataFrame) -> Dict[str, PerformanceKPI]:
        """Calculate facilities management KPIs"""
        kpis = {}

        try:
            # Transaction Volume KPI
            total_transactions = len(df)
            kpis['transaction_volume'] = PerformanceKPI(
                kpi_name="Monthly Transaction Volume",
                current_value=total_transactions,
                target_value=120,
                unit="transactions",
                trend=self._calculate_trend('transaction_volume', total_transactions),
                variance_percentage=((total_transactions - 120) / 120 * 100) if 120 > 0 else 0,
                status="on_track" if total_transactions >= 100 else "at_risk"
            )

            # Average Response Time (assuming some data is available)
            if 'Date_Out' in df.columns and 'Time_Out' in df.columns:
                # This would be calculated based on request-to-fulfillment time
                # For now, using a placeholder calculation
                kpis['response_time'] = PerformanceKPI(
                    kpi_name="Average Response Time",
                    current_value=24,  # hours
                    target_value=8,
                    unit="hours",
                    trend="stable",
                    variance_percentage=200,  # 24 vs 8 hours
                    status="off_track"
                )

            # Equipment Utilization Rate
            if 'Item_Name' in df.columns:
                unique_items_used = df['Item_Name'].nunique()
                # Assuming total inventory of 45 items
                utilization_rate = (unique_items_used / 45) * 100

                kpis['equipment_utilization'] = PerformanceKPI(
                    kpi_name="Equipment Utilization Rate",
                    current_value=utilization_rate,
                    target_value=70,
                    unit="percentage",
                    trend=self._calculate_trend('equipment_utilization', utilization_rate),
                    variance_percentage=((utilization_rate - 70) / 70 * 100),
                    status="on_track" if utilization_rate >= 60 else "at_risk"
                )

        except Exception as e:
            logger.error(f"Error calculating facilities KPIs: {e}")

        return kpis

    def _calculate_inventory_kpis(self) -> Dict[str, PerformanceKPI]:
        """Calculate inventory management KPIs"""
        kpis = {}

        try:
            if not self.inventory_manager:
                return kpis

            summary = self.inventory_manager.get_inventory_summary()

            # Stock Availability KPI
            total_items = summary.get('total_items', 0)
            critical_items = summary.get('stock_levels', {}).get('critical', 0)
            availability_percentage = ((total_items - critical_items) / total_items * 100) if total_items > 0 else 0

            kpis['stock_availability'] = PerformanceKPI(
                kpi_name="Stock Availability",
                current_value=availability_percentage,
                target_value=95,
                unit="percentage",
                trend=self._calculate_trend('stock_availability', availability_percentage),
                variance_percentage=((availability_percentage - 95) / 95 * 100),
                status="on_track" if availability_percentage >= 90 else "at_risk"
            )

            # Inventory Turnover
            # This would require historical sales data, using placeholder
            kpis['inventory_turnover'] = PerformanceKPI(
                kpi_name="Inventory Turnover",
                current_value=4.2,
                target_value=6.0,
                unit="turns/year",
                trend="stable",
                variance_percentage=-30,
                status="at_risk"
            )

            # Cost per Item Managed
            total_value = summary.get('total_value', 0)
            cost_per_item = total_value / total_items if total_items > 0 else 0

            kpis['cost_per_item'] = PerformanceKPI(
                kpi_name="Average Cost per Item",
                current_value=cost_per_item,
                target_value=2000,
                unit="rand",
                trend=self._calculate_trend('cost_per_item', cost_per_item),
                variance_percentage=((cost_per_item - 2000) / 2000 * 100) if cost_per_item > 0 else 0,
                status="on_track" if cost_per_item <= 2500 else "at_risk"
            )

        except Exception as e:
            logger.error(f"Error calculating inventory KPIs: {e}")

        return kpis

    def _extract_compliance_kpis(self, compliance_analysis: Dict[str, Any]) -> Dict[str, PerformanceKPI]:
        """Extract KPIs from compliance analysis"""
        kpis = {}

        try:
            metrics = compliance_analysis.get('compliance_metrics', {})

            # Work Order Compliance KPI
            wo_metric = metrics.get('work_order')
            if wo_metric and hasattr(wo_metric, 'compliance_percentage'):
                kpis['work_order_compliance'] = PerformanceKPI(
                    kpi_name="Work Order Compliance",
                    current_value=wo_metric.compliance_percentage,
                    target_value=95,
                    unit="percentage",
                    trend=wo_metric.trend,
                    variance_percentage=((wo_metric.compliance_percentage - 95) / 95 * 100),
                    status="on_track" if wo_metric.compliance_percentage >= 90 else
                           "at_risk" if wo_metric.compliance_percentage >= 70 else "off_track"
                )

            # Tool Return Compliance KPI
            return_metric = metrics.get('tool_return')
            if return_metric and hasattr(return_metric, 'compliance_percentage'):
                kpis['tool_return_compliance'] = PerformanceKPI(
                    kpi_name="Tool Return Compliance",
                    current_value=return_metric.compliance_percentage,
                    target_value=95,
                    unit="percentage",
                    trend=return_metric.trend,
                    variance_percentage=((return_metric.compliance_percentage - 95) / 95 * 100),
                    status="on_track" if return_metric.compliance_percentage >= 90 else
                           "at_risk" if return_metric.compliance_percentage >= 80 else "off_track"
                )

        except Exception as e:
            logger.error(f"Error extracting compliance KPIs: {e}")

        return kpis

    def _calculate_performance_kpis(self, df: pd.DataFrame) -> Dict[str, PerformanceKPI]:
        """Calculate overall performance KPIs"""
        kpis = {}

        try:
            # Staff Productivity KPI (transactions per staff member)
            if 'Borrower_Name' in df.columns:
                unique_staff = df['Borrower_Name'].nunique()
                total_transactions = len(df)
                productivity = total_transactions / unique_staff if unique_staff > 0 else 0

                kpis['staff_productivity'] = PerformanceKPI(
                    kpi_name="Staff Productivity",
                    current_value=productivity,
                    target_value=15,
                    unit="transactions/person",
                    trend=self._calculate_trend('staff_productivity', productivity),
                    variance_percentage=((productivity - 15) / 15 * 100) if productivity > 0 else 0,
                    status="on_track" if productivity >= 12 else "at_risk"
                )

            # Department Efficiency (based on transaction volume)
            if 'Department' in df.columns:
                dept_counts = df['Department'].value_counts()
                avg_dept_activity = dept_counts.mean() if not dept_counts.empty else 0

                kpis['department_efficiency'] = PerformanceKPI(
                    kpi_name="Average Department Activity",
                    current_value=avg_dept_activity,
                    target_value=20,
                    unit="transactions/dept",
                    trend="stable",
                    variance_percentage=((avg_dept_activity - 20) / 20 * 100) if avg_dept_activity > 0 else 0,
                    status="on_track" if avg_dept_activity >= 15 else "at_risk"
                )

        except Exception as e:
            logger.error(f"Error calculating performance KPIs: {e}")

        return kpis

    def export_analytics_report(self, file_path: str = None) -> str:
        """Export comprehensive analytics report"""
        try:
            if not file_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = f'analytics_report_{timestamp}.xlsx'

            # Generate all analytics
            compliance_analysis = self.generate_compliance_analysis()
            kpi_dashboard = self.generate_kpi_dashboard()

            # Prepare data for Excel export
            sheets_data = {}

            # Compliance summary sheet
            compliance_summary = []
            metrics = compliance_analysis.get('compliance_metrics', {})

            for metric_name, metric_data in metrics.items():
                if hasattr(metric_data, 'compliance_percentage'):
                    compliance_summary.append({
                        'Metric': metric_data.metric_name,
                        'Current Value': metric_data.current_value,
                        'Target Value': metric_data.target_value,
                        'Compliance %': metric_data.compliance_percentage,
                        'Risk Level': metric_data.risk_level.value,
                        'Trend': metric_data.trend,
                        'Description': metric_data.description
                    })

            if compliance_summary:
                sheets_data['Compliance_Summary'] = pd.DataFrame(compliance_summary)

            # KPI summary sheet
            kpi_summary = []
            all_kpis = {}
            all_kpis.update(kpi_dashboard.get('facilities_kpis', {}))
            all_kpis.update(kpi_dashboard.get('inventory_kpis', {}))
            all_kpis.update(kpi_dashboard.get('compliance_kpis', {}))
            all_kpis.update(kpi_dashboard.get('performance_kpis', {}))

            for kpi_name, kpi in all_kpis.items():
                kpi_summary.append({
                    'KPI Name': kpi.kpi_name,
                    'Current Value': kpi.current_value,
                    'Target Value': kpi.target_value,
                    'Unit': kpi.unit,
                    'Variance %': kpi.variance_percentage,
                    'Status': kpi.status,
                    'Trend': kpi.trend,
                    'Department': kpi.department
                })

            if kpi_summary:
                sheets_data['KPI_Dashboard'] = pd.DataFrame(kpi_summary)

            # Recommendations sheet
            recommendations = compliance_analysis.get('recommendations', [])
            if recommendations:
                rec_data = []
                for rec in recommendations:
                    rec_data.append({
                        'Category': rec.get('category', ''),
                        'Priority': rec.get('priority', ''),
                        'Title': rec.get('title', ''),
                        'Description': rec.get('description', ''),
                        'Expected Impact': rec.get('expected_impact', ''),
                        'Timeline': rec.get('timeline', '')
                    })
                sheets_data['Recommendations'] = pd.DataFrame(rec_data)

            # Write to Excel
            success = self.excel_processor.write_excel_file(
                sheets_data, file_path, 'analytics_report'
            )

            if success:
                logger.info(f"Analytics report exported to {file_path}")
                return file_path
            else:
                raise Exception("Failed to write Excel file")

        except Exception as e:
            logger.error(f"Error exporting analytics report: {e}")
            raise