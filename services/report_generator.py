#!/usr/bin/env python3
"""
Automated Report Generation System for Derivco Facilities Management
Generates comprehensive PDF and Excel reports with professional formatting
"""

import pandas as pd
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from datetime import datetime, timedelta
import os
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import json

# Import our core services
import sys
sys.path.append('core')
sys.path.append('services')
from excel_processor import AdvancedExcelProcessor
from inventory_service import AdvancedInventoryManager
from analytics_engine import RealTimeAnalyticsEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReportConfig:
    """Configuration for report generation"""
    report_type: str
    output_format: str  # 'pdf', 'excel', 'both'
    include_charts: bool = True
    include_analytics: bool = True
    include_recommendations: bool = True
    date_range: Optional[tuple] = None
    departments: Optional[List[str]] = None
    categories: Optional[List[str]] = None

class ProfessionalReportGenerator:
    """
    Advanced report generation system for Derivco facilities management
    Generates executive reports, operational dashboards, and compliance documentation
    """

    def __init__(self, excel_processor: AdvancedExcelProcessor = None,
                 inventory_manager: AdvancedInventoryManager = None,
                 analytics_engine: RealTimeAnalyticsEngine = None):

        self.excel_processor = excel_processor or AdvancedExcelProcessor()
        self.inventory_manager = inventory_manager
        self.analytics_engine = analytics_engine

        # Setup report directories
        self.reports_dir = Path('reports')
        self.reports_dir.mkdir(exist_ok=True)

        # Report templates and styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom report styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1e40af'),
            alignment=1  # Center
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#3b82f6'),
        ))

        # Executive summary style
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=15,
            leftIndent=20,
            rightIndent=20,
            backColor=colors.HexColor('#f0f9ff'),
            borderColor=colors.HexColor('#3b82f6'),
            borderWidth=1,
            borderPadding=10
        ))

    def generate_executive_dashboard_report(self, config: ReportConfig = None) -> str:
        """Generate comprehensive executive dashboard report"""
        try:
            logger.info("Generating executive dashboard report...")

            if not config:
                config = ReportConfig(
                    report_type='executive_dashboard',
                    output_format='pdf',
                    include_charts=True,
                    include_analytics=True,
                    include_recommendations=True
                )

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'executive_dashboard_{timestamp}.pdf'
            filepath = self.reports_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)

            # Build report content
            story = []

            # Title and header
            story.append(Paragraph("Derivco Facilities Management", self.styles['CustomTitle']))
            story.append(Paragraph("Executive Dashboard Report", self.styles['CustomSubtitle']))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                                 self.styles['Normal']))
            story.append(Spacer(1, 20))

            # Executive Summary
            exec_summary = self._generate_executive_summary()
            story.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
            story.append(Paragraph(exec_summary, self.styles['ExecutiveSummary']))
            story.append(Spacer(1, 20))

            # Key Performance Indicators
            if config.include_analytics and self.analytics_engine:
                kpi_data = self.analytics_engine.generate_kpi_dashboard()
                story.extend(self._add_kpi_section(kpi_data))

            # Inventory Overview
            if self.inventory_manager:
                inventory_summary = self.inventory_manager.get_inventory_summary()
                story.extend(self._add_inventory_section(inventory_summary))

            # Compliance Analysis
            if config.include_analytics and self.analytics_engine:
                compliance_data = self.analytics_engine.generate_compliance_analysis()
                story.extend(self._add_compliance_section(compliance_data))

            # Charts and Visualizations
            if config.include_charts:
                story.extend(self._add_charts_section())

            # Recommendations
            if config.include_recommendations and self.analytics_engine:
                compliance_data = self.analytics_engine.generate_compliance_analysis()
                recommendations = compliance_data.get('recommendations', [])
                story.extend(self._add_recommendations_section(recommendations))

            # Build PDF
            doc.build(story)

            logger.info(f"Executive dashboard report generated: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error generating executive dashboard report: {e}")
            raise

    def _generate_executive_summary(self) -> str:
        """Generate executive summary text"""
        try:
            summary_parts = []

            # Inventory summary
            if self.inventory_manager:
                inventory_summary = self.inventory_manager.get_inventory_summary()
                total_value = inventory_summary.get('total_value', 0)
                total_items = inventory_summary.get('total_items', 0)
                critical_items = inventory_summary.get('stock_levels', {}).get('critical', 0)

                summary_parts.append(f"Our facilities currently manage {total_items:,} inventory items "
                                    f"valued at R{total_value:,.2f}. ")

                if critical_items > 0:
                    summary_parts.append(f"ATTENTION REQUIRED: {critical_items} items are at critical stock levels. ")

            # Compliance summary
            if self.analytics_engine:
                try:
                    compliance_analysis = self.analytics_engine.generate_compliance_analysis()
                    metrics = compliance_analysis.get('compliance_metrics', {})

                    wo_metric = metrics.get('work_order')
                    if wo_metric and hasattr(wo_metric, 'compliance_percentage'):
                        wo_compliance = wo_metric.compliance_percentage
                        summary_parts.append(f"Work order compliance currently at {wo_compliance:.1f}%. ")

                        if wo_compliance < 60:
                            summary_parts.append("CRITICAL: Immediate action required to address compliance gaps. ")

                    return_metric = metrics.get('tool_return')
                    if return_metric and hasattr(return_metric, 'compliance_percentage'):
                        return_compliance = return_metric.compliance_percentage
                        summary_parts.append(f"Tool return compliance at {return_compliance:.1f}%. ")

                except Exception as e:
                    logger.warning(f"Could not generate compliance summary: {e}")

            # Business impact
            summary_parts.append("This report provides comprehensive analysis of our facilities management "
                                "performance, identifies key risks, and recommends actionable improvements "
                                "to enhance operational efficiency and compliance.")

            return " ".join(summary_parts)

        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return "Executive summary generation in progress. Please review detailed sections below."

    def _add_kpi_section(self, kpi_data: Dict[str, Any]) -> List:
        """Add KPI section to report"""
        content = []

        content.append(Paragraph("Key Performance Indicators", self.styles['CustomSubtitle']))

        # Create KPI table
        kpi_table_data = [['KPI Category', 'Metric', 'Current', 'Target', 'Status']]

        all_kpis = {}
        all_kpis.update(kpi_data.get('facilities_kpis', {}))
        all_kpis.update(kpi_data.get('inventory_kpis', {}))
        all_kpis.update(kpi_data.get('compliance_kpis', {}))

        for category, kpi in all_kpis.items():
            status_color = 'green' if kpi.status == 'on_track' else 'orange' if kpi.status == 'at_risk' else 'red'
            kpi_table_data.append([
                category.replace('_', ' ').title(),
                kpi.kpi_name,
                f"{kpi.current_value:.1f} {kpi.unit}",
                f"{kpi.target_value:.1f} {kpi.unit}",
                kpi.status.replace('_', ' ').title()
            ])

        if len(kpi_table_data) > 1:
            kpi_table = Table(kpi_table_data)
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
            ]))
            content.append(kpi_table)

        content.append(Spacer(1, 20))
        return content

    def _add_inventory_section(self, inventory_summary: Dict[str, Any]) -> List:
        """Add inventory analysis section"""
        content = []

        content.append(Paragraph("Inventory Analysis", self.styles['CustomSubtitle']))

        # Inventory summary table
        inv_data = [
            ['Total Items', f"{inventory_summary.get('total_items', 0):,}"],
            ['Total Value', f"R{inventory_summary.get('total_value', 0):,.2f}"],
            ['Categories', f"{len(inventory_summary.get('categories', {})):,}"],
            ['Low Stock Items', f"{inventory_summary.get('stock_levels', {}).get('low', 0) + inventory_summary.get('stock_levels', {}).get('critical', 0):,}"]
        ]

        inv_table = Table(inv_data, colWidths=[2*inch, 2*inch])
        inv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f1f5f9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
        ]))

        content.append(inv_table)
        content.append(Spacer(1, 15))

        # Category breakdown
        categories = inventory_summary.get('categories', {})
        if categories:
            content.append(Paragraph("Inventory by Category", self.styles['Heading3']))

            cat_data = [['Category', 'Items', 'Value', 'Low Stock']]
            for cat_name, cat_stats in categories.items():
                cat_data.append([
                    cat_name,
                    f"{cat_stats.get('item_count', 0):,}",
                    f"R{cat_stats.get('total_value', 0):,.2f}",
                    f"{cat_stats.get('low_stock_items', 0):,}"
                ])

            cat_table = Table(cat_data)
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
            ]))
            content.append(cat_table)

        content.append(Spacer(1, 20))
        return content

    def _add_compliance_section(self, compliance_data: Dict[str, Any]) -> List:
        """Add compliance analysis section"""
        content = []

        content.append(Paragraph("Compliance Analysis", self.styles['CustomSubtitle']))

        # Compliance metrics table
        metrics = compliance_data.get('compliance_metrics', {})
        comp_data = [['Compliance Area', 'Current %', 'Target %', 'Risk Level']]

        wo_metric = metrics.get('work_order')
        if wo_metric and hasattr(wo_metric, 'compliance_percentage'):
            risk_color = 'red' if wo_metric.risk_level.value == 'critical' else 'orange' if wo_metric.risk_level.value == 'high' else 'green'
            comp_data.append([
                'Work Order Compliance',
                f"{wo_metric.compliance_percentage:.1f}%",
                f"{wo_metric.target_value:.1f}%",
                wo_metric.risk_level.value.title()
            ])

        return_metric = metrics.get('tool_return')
        if return_metric and hasattr(return_metric, 'compliance_percentage'):
            risk_color = 'red' if return_metric.risk_level.value == 'critical' else 'orange' if return_metric.risk_level.value == 'high' else 'green'
            comp_data.append([
                'Tool Return Compliance',
                f"{return_metric.compliance_percentage:.1f}%",
                f"{return_metric.target_value:.1f}%",
                return_metric.risk_level.value.title()
            ])

        if len(comp_data) > 1:
            comp_table = Table(comp_data)
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fecaca'))
            ]))
            content.append(comp_table)

        # Risk assessment
        risk_assessment = compliance_data.get('risk_assessment', {})
        if risk_assessment:
            overall_risk = risk_assessment.get('overall_risk_level', 'unknown')
            content.append(Spacer(1, 10))
            content.append(Paragraph(f"Overall Risk Level: {overall_risk.title()}",
                                   self.styles['Heading3']))

            risk_factors = risk_assessment.get('risk_factors', [])
            if risk_factors:
                for risk in risk_factors[:3]:  # Top 3 risks
                    risk_text = f"• {risk.get('factor', '')}: {risk.get('impact', '')}"
                    content.append(Paragraph(risk_text, self.styles['Normal']))

        content.append(Spacer(1, 20))
        return content

    def _add_charts_section(self) -> List:
        """Add charts and visualizations section"""
        content = []

        content.append(Paragraph("Performance Visualizations", self.styles['CustomSubtitle']))

        # Note: In production, you would generate actual charts here
        # For now, adding placeholder for chart space
        content.append(Paragraph("📊 Chart visualizations would be rendered here in production deployment.",
                                self.styles['Normal']))
        content.append(Paragraph("• Inventory value distribution by category", self.styles['Normal']))
        content.append(Paragraph("• Compliance trends over time", self.styles['Normal']))
        content.append(Paragraph("• Department performance comparison", self.styles['Normal']))
        content.append(Paragraph("• Stock level distribution", self.styles['Normal']))

        content.append(Spacer(1, 20))
        return content

    def _add_recommendations_section(self, recommendations: List[Dict]) -> List:
        """Add recommendations section"""
        content = []

        content.append(Paragraph("Strategic Recommendations", self.styles['CustomSubtitle']))

        if not recommendations:
            content.append(Paragraph("No specific recommendations at this time. System operating within acceptable parameters.",
                                   self.styles['Normal']))
        else:
            for i, rec in enumerate(recommendations[:5], 1):  # Top 5 recommendations
                rec_title = f"{i}. {rec.get('title', 'Recommendation')}"
                content.append(Paragraph(rec_title, self.styles['Heading3']))

                content.append(Paragraph(f"Priority: {rec.get('priority', 'medium').title()}",
                                       self.styles['Normal']))
                content.append(Paragraph(f"Description: {rec.get('description', '')}",
                                       self.styles['Normal']))
                content.append(Paragraph(f"Expected Impact: {rec.get('expected_impact', '')}",
                                       self.styles['Normal']))
                content.append(Paragraph(f"Timeline: {rec.get('timeline', '')}",
                                       self.styles['Normal']))
                content.append(Spacer(1, 10))

        content.append(Spacer(1, 20))
        return content

    def generate_operational_report(self, config: ReportConfig = None) -> str:
        """Generate detailed operational report"""
        try:
            logger.info("Generating operational report...")

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'operational_report_{timestamp}.xlsx'
            filepath = self.reports_dir / filename

            # Collect all operational data
            report_data = {}

            # Inventory data
            if self.inventory_manager:
                items_data = []
                for item in self.inventory_manager.items.values():
                    items_data.append({
                        'Item Code': item.item_code,
                        'Item Name': item.item_name,
                        'Category': item.category,
                        'Quantity': item.quantity,
                        'Unit Price': item.unit_price,
                        'Total Value': item.total_value,
                        'Supplier': item.supplier,
                        'Stock Level': item.stock_level_category.value,
                        'Reorder Level': item.reorder_level,
                        'Usage Rate': item.usage_rate,
                        'Last Updated': item.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                    })
                report_data['Inventory_Detail'] = pd.DataFrame(items_data)

                # Low stock items
                low_stock = self.inventory_manager.get_low_stock_items()
                low_stock_data = []
                for item in low_stock:
                    low_stock_data.append({
                        'Item Code': item.item_code,
                        'Item Name': item.item_name,
                        'Category': item.category,
                        'Current Stock': item.quantity,
                        'Reorder Level': item.reorder_level,
                        'Supplier': item.supplier,
                        'Unit Price': item.unit_price,
                        'Priority': 'Critical' if item.quantity <= 5 else 'High'
                    })
                if low_stock_data:
                    report_data['Low_Stock_Items'] = pd.DataFrame(low_stock_data)

                # Reorder recommendations
                recommendations = self.inventory_manager.generate_reorder_recommendations()
                if recommendations:
                    report_data['Reorder_Recommendations'] = pd.DataFrame(recommendations)

            # Compliance data
            if self.analytics_engine:
                try:
                    compliance_analysis = self.analytics_engine.generate_compliance_analysis()

                    # Extract recommendations
                    rec_data = []
                    for rec in compliance_analysis.get('recommendations', []):
                        rec_data.append({
                            'Category': rec.get('category', ''),
                            'Priority': rec.get('priority', ''),
                            'Title': rec.get('title', ''),
                            'Description': rec.get('description', ''),
                            'Expected Impact': rec.get('expected_impact', ''),
                            'Timeline': rec.get('timeline', '')
                        })
                    if rec_data:
                        report_data['Compliance_Recommendations'] = pd.DataFrame(rec_data)

                except Exception as e:
                    logger.warning(f"Could not generate compliance data for operational report: {e}")

            # Write Excel file
            if report_data:
                success = self.excel_processor.write_excel_file(
                    report_data, str(filepath), 'operational_report'
                )

                if success:
                    logger.info(f"Operational report generated: {filepath}")
                    return str(filepath)
                else:
                    raise Exception("Failed to write operational report")
            else:
                raise Exception("No data available for operational report")

        except Exception as e:
            logger.error(f"Error generating operational report: {e}")
            raise

    def generate_compliance_audit_report(self) -> str:
        """Generate comprehensive compliance audit report"""
        try:
            logger.info("Generating compliance audit report...")

            if not self.analytics_engine:
                raise Exception("Analytics engine required for compliance audit report")

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'compliance_audit_{timestamp}.pdf'
            filepath = self.reports_dir / filename

            # Generate compliance analysis
            compliance_analysis = self.analytics_engine.generate_compliance_analysis()

            # Create PDF document
            doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)

            story = []

            # Title
            story.append(Paragraph("Derivco Facilities Management", self.styles['CustomTitle']))
            story.append(Paragraph("Compliance Audit Report", self.styles['CustomSubtitle']))
            story.append(Paragraph(f"Audit Date: {datetime.now().strftime('%B %d, %Y')}",
                                 self.styles['Normal']))
            story.append(Spacer(1, 30))

            # Executive Summary
            risk_assessment = compliance_analysis.get('risk_assessment', {})
            overall_risk = risk_assessment.get('overall_risk_level', 'unknown')

            exec_summary = f"This compliance audit reveals an overall risk level of {overall_risk.upper()}. "
            exec_summary += "Detailed findings and recommendations are provided below for immediate management action."

            story.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
            story.append(Paragraph(exec_summary, self.styles['ExecutiveSummary']))
            story.append(Spacer(1, 20))

            # Detailed compliance metrics
            story.extend(self._add_compliance_section(compliance_analysis))

            # Recommendations with detailed action plans
            recommendations = compliance_analysis.get('recommendations', [])
            story.extend(self._add_recommendations_section(recommendations))

            # Business impact analysis
            business_impact = compliance_analysis.get('business_impact', {})
            if business_impact:
                story.append(Paragraph("Business Impact Analysis", self.styles['CustomSubtitle']))

                financial_impact = business_impact.get('financial_impact', {})
                for impact_type, impact_data in financial_impact.items():
                    if isinstance(impact_data, dict):
                        monthly = impact_data.get('monthly_estimate', 0)
                        annual = impact_data.get('annual_estimate', 0)
                        description = impact_data.get('description', '')

                        story.append(Paragraph(f"{impact_type.replace('_', ' ').title()}",
                                             self.styles['Heading3']))
                        story.append(Paragraph(f"Monthly Impact: R{monthly:,.2f}",
                                             self.styles['Normal']))
                        story.append(Paragraph(f"Annual Impact: R{annual:,.2f}",
                                             self.styles['Normal']))
                        story.append(Paragraph(f"Description: {description}",
                                             self.styles['Normal']))
                        story.append(Spacer(1, 10))

            # Build PDF
            doc.build(story)

            logger.info(f"Compliance audit report generated: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error generating compliance audit report: {e}")
            raise

    def generate_monthly_summary(self, year: int = None, month: int = None) -> str:
        """Generate monthly summary report"""
        try:
            if not year:
                year = datetime.now().year
            if not month:
                month = datetime.now().month

            logger.info(f"Generating monthly summary for {year}-{month:02d}")

            filename = f'monthly_summary_{year}_{month:02d}.pdf'
            filepath = self.reports_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)

            story = []

            # Title
            month_name = datetime(year, month, 1).strftime('%B %Y')
            story.append(Paragraph("Derivco Facilities Management", self.styles['CustomTitle']))
            story.append(Paragraph(f"Monthly Summary - {month_name}", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 30))

            # Monthly highlights
            story.append(Paragraph("Monthly Highlights", self.styles['CustomSubtitle']))

            highlights = []
            if self.inventory_manager:
                inventory_summary = self.inventory_manager.get_inventory_summary()
                total_value = inventory_summary.get('total_value', 0)
                highlights.append(f"• Total inventory value: R{total_value:,.2f}")

                critical_items = inventory_summary.get('stock_levels', {}).get('critical', 0)
                if critical_items > 0:
                    highlights.append(f"• {critical_items} items require immediate attention")
                else:
                    highlights.append("• All inventory items adequately stocked")

            if self.analytics_engine:
                try:
                    compliance_analysis = self.analytics_engine.generate_compliance_analysis()
                    metrics = compliance_analysis.get('compliance_metrics', {})

                    wo_metric = metrics.get('work_order')
                    if wo_metric and hasattr(wo_metric, 'compliance_percentage'):
                        highlights.append(f"• Work order compliance: {wo_metric.compliance_percentage:.1f}%")

                    return_metric = metrics.get('tool_return')
                    if return_metric and hasattr(return_metric, 'compliance_percentage'):
                        highlights.append(f"• Tool return compliance: {return_metric.compliance_percentage:.1f}%")

                except Exception as e:
                    logger.warning(f"Could not load compliance metrics for monthly summary: {e}")

            for highlight in highlights:
                story.append(Paragraph(highlight, self.styles['Normal']))

            story.append(Spacer(1, 20))

            # Add other sections
            if self.inventory_manager:
                inventory_summary = self.inventory_manager.get_inventory_summary()
                story.extend(self._add_inventory_section(inventory_summary))

            if self.analytics_engine:
                try:
                    compliance_analysis = self.analytics_engine.generate_compliance_analysis()
                    story.extend(self._add_compliance_section(compliance_analysis))
                except Exception as e:
                    logger.warning(f"Could not add compliance section to monthly summary: {e}")

            # Build PDF
            doc.build(story)

            logger.info(f"Monthly summary generated: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error generating monthly summary: {e}")
            raise

    def schedule_automated_reports(self):
        """Setup automated report generation schedule"""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger

            scheduler = BackgroundScheduler()

            # Daily operational report (8 AM)
            scheduler.add_job(
                func=self._generate_daily_operational_report,
                trigger=CronTrigger(hour=8, minute=0),
                id='daily_operational_report',
                replace_existing=True
            )

            # Weekly executive report (Monday 9 AM)
            scheduler.add_job(
                func=self._generate_weekly_executive_report,
                trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),
                id='weekly_executive_report',
                replace_existing=True
            )

            # Monthly compliance audit (1st day of month, 10 AM)
            scheduler.add_job(
                func=self._generate_monthly_compliance_audit,
                trigger=CronTrigger(day=1, hour=10, minute=0),
                id='monthly_compliance_audit',
                replace_existing=True
            )

            scheduler.start()
            logger.info("Automated report scheduling configured")

        except ImportError:
            logger.warning("APScheduler not available - automated reports disabled")
        except Exception as e:
            logger.error(f"Error setting up automated reports: {e}")

    def _generate_daily_operational_report(self):
        """Generate daily operational report (automated)"""
        try:
            config = ReportConfig(
                report_type='daily_operational',
                output_format='excel',
                include_charts=False,
                include_analytics=True
            )
            filepath = self.generate_operational_report(config)
            logger.info(f"Automated daily operational report generated: {filepath}")
        except Exception as e:
            logger.error(f"Error in automated daily report: {e}")

    def _generate_weekly_executive_report(self):
        """Generate weekly executive report (automated)"""
        try:
            filepath = self.generate_executive_dashboard_report()
            logger.info(f"Automated weekly executive report generated: {filepath}")
        except Exception as e:
            logger.error(f"Error in automated weekly report: {e}")

    def _generate_monthly_compliance_audit(self):
        """Generate monthly compliance audit (automated)"""
        try:
            filepath = self.generate_compliance_audit_report()
            logger.info(f"Automated monthly compliance audit generated: {filepath}")
        except Exception as e:
            logger.error(f"Error in automated monthly audit: {e}")

    def get_available_reports(self) -> List[Dict[str, Any]]:
        """Get list of available generated reports"""
        try:
            reports = []

            for file_path in self.reports_dir.glob('*'):
                if file_path.is_file() and file_path.suffix in ['.pdf', '.xlsx']:
                    stat = file_path.stat()
                    reports.append({
                        'filename': file_path.name,
                        'filepath': str(file_path),
                        'size_mb': stat.st_size / (1024 * 1024),
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': file_path.suffix[1:].upper()
                    })

            # Sort by creation date (newest first)
            reports.sort(key=lambda x: x['created'], reverse=True)
            return reports

        except Exception as e:
            logger.error(f"Error getting available reports: {e}")
            return []

    def cleanup_old_reports(self, days_to_keep: int = 30):
        """Clean up old report files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0

            for file_path in self.reports_dir.glob('*'):
                if file_path.is_file():
                    file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_date < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1

            logger.info(f"Cleaned up {deleted_count} old report files")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up old reports: {e}")
            return 0