"""
PDF Report Generators for Compliance Reports
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import io
import logging

logger = logging.getLogger(__name__)


class ComplianceReportGenerator:
    """Generate compliance reports in PDF format"""

    def __init__(self):
        self._setup_fonts()
        self._setup_styles()

    def _setup_fonts(self):
        """Register custom fonts"""
        # Try to use system fonts, fall back to default
        try:
            pdfmetrics.registerFont(TTFont('Roboto', '/usr/share/fonts/truetype/roboto/Roboto-Regular.ttf'))
            pdfmetrics.registerFont(TTFont('Roboto-Bold', '/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf'))
        except:
            # Use default fonts if custom fonts not available
            logger.warning("Custom fonts not available, using defaults")

    def _setup_styles(self):
        """Setup report styles"""
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parentName='Title',
            fontSize=24,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parentName='Heading2',
            fontSize=16,
            textColor=colors.HexColor('#1B5E20'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='RightAligned',
            parentName='Normal',
            alignment=TA_RIGHT
        ))

    def generate_inspection_report(
        self,
        restaurant_data: Dict,
        inspection_history: List[Dict],
        readings_data: List[Dict],
        alerts_data: List[Dict]
    ) -> bytes:
        """Generate comprehensive inspection compliance report"""

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        # Build story (content)
        story = []

        # 1. Title Page
        story.extend(self._create_title_page(restaurant_data))

        # 2. Executive Summary
        story.append(PageBreak())
        story.extend(self._create_executive_summary(restaurant_data, inspection_history))

        # 3. Inspection History
        story.append(PageBreak())
        story.extend(self._create_inspection_history_section(inspection_history))

        # 4. Sensor Data Analysis
        story.append(PageBreak())
        story.extend(self._create_sensor_data_section(readings_data))

        # 5. Alerts & Violations
        story.append(PageBreak())
        story.extend(self._create_alerts_section(alerts_data))

        # 6. Recommendations
        story.append(PageBreak())
        story.extend(self._create_recommendations(restaurant_data, inspection_history, alerts_data))

        # 7. Appendix
        story.append(PageBreak())
        story.extend(self._create_appendix(inspection_history))

        # Build PDF
        doc.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def _create_title_page(self, restaurant_data: Dict) -> list:
        """Create title page"""
        story = []

        # Main title
        story.append(Spacer(2*inch))
        story.append(Paragraph("HealthGuard Compliance Report", self.styles['CustomTitle']))

        # Subtitle
        story.append(Paragraph(
            f"Restaurant Compliance Monitoring & Analysis",
            self.styles['Heading3']
        ))

        story.append(Spacer(0.5*inch))

        # Restaurant info
        story.append(Paragraph(f"<b>Restaurant:</b> {restaurant_data.get('name', 'N/A')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Address:</b> {restaurant_data.get('address', 'N/A')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>City:</b> {restaurant_data.get('city', 'N/A')}, {restaurant_data.get('state', 'N/A')}", self.styles['Normal']))

        story.append(Spacer(0.5*inch))

        # Report date
        report_date = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"<b>Report Generated:</b> {report_date}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Period Covered:</b> Last 90 days", self.styles['Normal']))

        story.append(Spacer(2*inch))

        # Compliance Score (large)
        score = restaurant_data.get('compliance_score', 0)
        score_color = self._get_score_color(score)

        story.append(Paragraph("Overall Compliance Score", ParagraphStyle(
            name='ScoreLabel',
            parentName='Normal',
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=10
        )))

        story.append(Paragraph(
            f"{score:.1f}%",
            ParagraphStyle(
                name='ScoreValue',
                parentName='Title',
                fontSize=72,
                textColor=score_color,
                alignment=TA_CENTER,
                spaceAfter=20
            )
        ))

        # Disclaimer
        story.append(Spacer(1.5*inch))
        story.append(Paragraph(
            "<i>This report is based on automated monitoring data and public inspection records. "
            "It should be used as a tool for improvement and not as a substitute for "
            "professional food safety guidance.</i>",
            ParagraphStyle(
                name='Disclaimer',
                parentName='Normal',
                fontSize=8,
                fontName='Helvetica-Oblique',
                alignment=TA_CENTER,
                textColor=colors.grey
            )
        ))

        return story

    def _create_executive_summary(self, restaurant_data: Dict, inspection_history: List[Dict]) -> list:
        """Create executive summary section"""
        story = []

        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        # Summary stats
        if inspection_history:
            latest_inspection = max(inspection_history, key=lambda x: x.get('inspection_date', datetime.min))
            latest_score = latest_inspection.get('score', 'N/A')
            latest_date = latest_inspection.get('inspection_date')

            # Summary table
            summary_data = [
                ['Metric', 'Value'],
                ['Latest Inspection Score', f"{latest_score or 'N/A'}"],
                ['Latest Inspection Date', f"{latest_date.strftime('%B %d, %Y') if latest_date else 'N/A'}"],
                ['Compliance Score (90-day)', f"{restaurant_data.get('compliance_score', 0):.1f}%"],
                ['Active Sensors', f"{restaurant_data.get('active_devices', 0)}"],
                ['Total Alerts (90-day)', f"{len(restaurant_data.get('alerts', []))}"],
                ['Critical Alerts', f"{restaurant_data.get('critical_alerts', 0)}"],
            ]

            table = Table(summary_data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#2E7D32')),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            story.append(table)
            story.append(Spacer(0.25*inch))

        # Key findings
        story.append(Paragraph("Key Findings", self.styles['Heading3']))

        findings = self._generate_key_findings(restaurant_data, inspection_history)

        for i, finding in enumerate(findings, 1):
            story.append(Paragraph(f"{i}. {finding}", self.styles['Normal'], bulletIndent=20))

        return story

    def _create_inspection_history_section(self, inspection_history: List[Dict]) -> list:
        """Create inspection history section"""
        story = []

        story.append(Paragraph("Health Inspection History", self.styles['SectionHeader']))
        story.append(Spacer(0.2*inch))

        if not inspection_history:
            story.append(Paragraph("No inspection history available.", self.styles['Normal']))
            return story

        # Sort by date descending
        sorted_inspections = sorted(
            inspection_history,
            key=lambda x: x.get('inspection_date', datetime.min),
            reverse=True
        )

        for inspection in sorted_inspections[:10]:  # Last 10 inspections
            insp_date = inspection.get('inspection_date')
            score = inspection.get('score')
            grade = inspection.get('grade')
            violations = inspection.get('violations', [])

            # Inspection header
            story.append(Paragraph(
                f"<b>{insp_date.strftime('%B %d, %Y') if insp_date else 'Unknown Date'}</b> "
                f"- Score: {score or 'N/A'} "
                f"{'Grade: ' + grade if grade else ''}",
                ParagraphStyle(
                    name='InspectionHeader',
                    parentName='Normal',
                    fontSize=12,
                    fontName='Helvetica-Bold',
                    spaceAfter=8
                )
            ))

            # Violations
            if violations:
                for violation in violations[:5]:  # Show first 5 violations
                    severity = violation.get('severity', 'info')
                    description = violation.get('description', 'No description')

                    # Color code by severity
                    if severity == 'critical':
                        color = colors.red
                    elif severity == 'warning':
                        color = colors.orange
                    else:
                        color = colors.black

                    story.append(Paragraph(
                        f"• {description}",
                        ParagraphStyle(
                            name='ViolationText',
                            parentName='Normal',
                            fontSize=10,
                            leftIndent=20,
                            textColor=color,
                            spaceAfter=4
                        )
                    ))

                if len(violations) > 5:
                    story.append(Paragraph(
                        f"... and {len(violations) - 5} more violations",
                        ParagraphStyle(
                            name='MoreViolations',
                            parentName='Normal',
                            fontSize=10,
                            leftIndent=20,
                            textColor=colors.grey,
                            spaceAfter=12
                        )
                    ))
            else:
                story.append(Paragraph(
                    "No violations recorded - Excellent!",
                    ParagraphStyle(
                        name='NoViolations',
                        parentName='Normal',
                        fontSize=10,
                        leftIndent=20,
                        textColor=colors.HexColor('#2E7D32'),
                        spaceAfter=12
                    )
                ))

        return story

    def _create_sensor_data_section(self, readings_data: List[Dict]) -> list:
        """Create sensor data analysis section"""
        story = []

        story.append(Paragraph("Sensor Monitoring Data", self.styles['SectionHeader']))
        story.append(Spacer(0.2*inch))

        if not readings_data:
            story.append(Paragraph("No sensor data available for this period.", self.styles['Normal']))
            return story

        # Summary statistics
        temps = [r.get('temperature') for r in readings_data if r.get('temperature') is not None]

        if temps:
            avg_temp = sum(temps) / len(temps)
            min_temp = min(temps)
            max_temp = max(temps)

            stats_data = [
                ['Metric', 'Value'],
                ['Total Readings', f"{len(readings_data):,}"],
                ['Average Temperature', f"{avg_temp:.1f}°F"],
                ['Min Temperature', f"{min_temp:.1f}°F"],
                ['Max Temperature', f"{max_temp:.1f}°F"],
                ['Temperature Range', f"{max_temp - min_temp:.1f}°F"],
            ]

            table = Table(stats_data, colWidths=[2.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            story.append(table)
            story.append(Spacer(0.25*inch))

        # Sensor breakdown
        story.append(Paragraph("Sensor Breakdown", self.styles['Heading3']))

        # Group by device
        from collections import defaultdict
        device_stats = defaultdict(lambda: {'count': 0, 'temps': []})

        for reading in readings_data:
            device_id = reading.get('device_id', 'unknown')
            device_stats[device_id]['count'] += 1
            if reading.get('temperature'):
                device_stats[device_id]['temps'].append(reading['temperature'])

        # Device table
        device_data = [['Device', 'Readings', 'Avg Temp', 'Min Temp', 'Max Temp']]

        for device_id, stats in sorted(device_stats.items()):
            if stats['temps']:
                avg = sum(stats['temps']) / len(stats['temps'])
                min_t = min(stats['temps'])
                max_t = max(stats['temps'])
            else:
                avg = min_t = max_t = 'N/A'

            device_data.append([
                device_id,
                f"{stats['count']:,}",
                f"{avg:.1f}°F" if avg != 'N/A' else 'N/A',
                f"{min_t:.1f}°F" if min_t != 'N/A' else 'N/A',
                f"{max_t:.1f}°F" if max_t != 'N/A' else 'N/A'
            ])

        device_table = Table(device_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        device_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), (colors.white, colors.lightgrey)),
        ]))

        story.append(device_table)

        return story

    def _create_alerts_section(self, alerts_data: List[Dict]) -> list:
        """Create alerts and violations section"""
        story = []

        story.append(Paragraph("Alerts & Compliance Issues", self.styles['SectionHeader']))
        story.append(Spacer(0.2*inch))

        if not alerts_data:
            story.append(Paragraph("No alerts recorded for this period. Excellent work!", self.styles['Normal']))
            return story

        # Summary by severity
        critical = [a for a in alerts_data if a.get('severity') == 'CRITICAL']
        warning = [a for a in alerts_data if a.get('severity') == 'WARNING']
        info = [a for a in alerts_data if a.get('severity') == 'INFO']

        summary_data = [
            ['Severity', 'Count'],
            ['Critical', f"{len(critical)}"],
            ['Warning', f"{len(warning)}"],
            ['Info', f"{len(info)}"],
            ['Total', f"{len(alerts_data)}"],
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 0), (0, -1), colors.white, colors.lightgrey),
        ]))

        story.append(summary_table)
        story.append(Spacer(0.25*inch))

        # Critical alerts details
        if critical:
            story.append(Paragraph("Critical Alerts (Require Immediate Attention)", self.styles['Heading3']))

            for alert in critical[:10]:  # Show first 10
                timestamp = alert.get('created_at', '')
                title = alert.get('title', 'Unnamed Alert')
                message = alert.get('message', '')

                story.append(Paragraph(
                    f"<b>{timestamp.strftime('%Y-%m-%d %H:%M') if isinstance(timestamp, datetime) else timestamp}</b> - {title}",
                    ParagraphStyle(
                        name='CriticalAlert',
                        parentName='Normal',
                        fontSize=10,
                        fontName='Helvetica-Bold',
                        textColor=colors.red,
                        spaceAfter=4
                    )
                ))
                story.append(Paragraph(
                    message,
                    ParagraphStyle(
                        name='CriticalAlertMsg',
                        parentName='Normal',
                        fontSize=9,
                        leftIndent=20,
                        spaceAfter=10
                    )
                ))

        return story

    def _create_recommendations(self, restaurant_data: Dict, inspection_history: List[Dict], alerts_data: List[Dict]) -> list:
        """Create recommendations section"""
        story = []

        story.append(Paragraph("Recommendations for Improvement", self.styles['SectionHeader']))
        story.append(Spacer(0.2*inch))

        recommendations = self._generate_recommendations(restaurant_data, inspection_history, alerts_data)

        for i, rec in enumerate(recommendations, 1):
            # Category
            category = rec.get('category', 'General')
            priority = rec.get('priority', 'Medium')
            title = rec.get('title', '')
            description = rec.get('description', '')

            priority_color = {
                'High': colors.red,
                'Medium': colors.orange,
                'Low': colors.HexColor('#2E7D32')
            }.get(priority, colors.black)

            story.append(Paragraph(
                f"{i}. {title}",
                ParagraphStyle(
                    name='RecTitle',
                    parentName='Normal',
                    fontSize=12,
                    fontName='Helvetica-Bold',
                    textColor=priority_color,
                    spaceAfter=4
                )
            ))

            story.append(Paragraph(
                f"Priority: {priority} | Category: {category}",
                ParagraphStyle(
                    name='RecMeta',
                    parentName='Normal',
                    fontSize=9,
                    textColor=colors.grey,
                    spaceAfter=4
                )
            ))

            story.append(Paragraph(
                description,
                ParagraphStyle(
                    name='RecDesc',
                    parentName='Normal',
                    fontSize=10,
                    leftIndent=20,
                    spaceAfter=16
                )
            ))

        return story

    def _create_appendix(self, inspection_history: List[Dict]) -> list:
        """Create appendix with additional data"""
        story = []

        story.append(Paragraph("Appendix", self.styles['SectionHeader']))
        story.append(Spacer(0.2*inch))

        # Report metadata
        story.append(Paragraph("A. Report Metadata", self.styles['Heading3']))

        metadata_data = [
            ['Report Type', 'Compliance Summary Report'],
            ['Generated', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['Report Period', 'Last 90 days'],
            ['Data Sources', 'Automated sensors, public records'],
            ['Version', '1.0'],
        ]

        metadata_table = Table(metadata_data, colWidths=[2*inch, 3*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), (colors.white, colors.lightgrey)),
        ]))

        story.append(metadata_table)

        return story

    def _generate_key_findings(self, restaurant_data: Dict, inspection_history: List[Dict]) -> List[str]:
        """Generate key findings for executive summary"""
        findings = []

        score = restaurant_data.get('compliance_score', 0)

        if score >= 90:
            findings.append(f"Excellent compliance score of {score:.1f}%, indicating strong food safety practices.")
        elif score >= 70:
            findings.append(f"Good compliance score of {score:.1f}%, with room for improvement in specific areas.")
        elif score >= 50:
            findings.append(f"Moderate compliance score of {score:.1f}%. Attention needed in critical areas.")
        else:
            findings.append(f"Low compliance score of {score:.1f}%. Immediate action required to avoid violations.")

        # Latest inspection
        if inspection_history:
            latest = max(inspection_history, key=lambda x: x.get('inspection_date', datetime.min))
            latest_score = latest.get('score')

            if latest_score and latest_score < 70:
                findings.append(f"Most recent health inspection scored {latest_score}, below recommended threshold.")
            elif latest_score and latest_score >= 90:
                findings.append(f"Most recent inspection scored {latest_score}, demonstrating excellence.")

        # Alerts
        critical_alerts = restaurant_data.get('critical_alerts', 0)
        if critical_alerts > 0:
            findings.append(f"{critical_alerts} critical alerts require immediate attention.")
        else:
            findings.append("No critical compliance issues detected in the last 90 days.")

        # Sensors
        active_sensors = restaurant_data.get('active_devices', 0)
        if active_sensors > 0:
            findings.append(f"{active_sensors} active monitoring sensors providing real-time compliance data.")

        if not findings:
            findings.append("Insufficient data available to generate findings.")

        return findings

    def _generate_recommendations(self, restaurant_data: Dict, inspection_history: List[Dict], alerts_data: List[Dict]) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []

        score = restaurant_data.get('compliance_score', 0)

        # Based on overall score
        if score < 70:
            recommendations.append({
                'category': 'Critical',
                'priority': 'High',
                'title': 'Improve Overall Compliance Score',
                'description': 'Your compliance score is below 70%. Implement daily monitoring logs, ensure all staff complete food safety training, and conduct weekly self-inspections to identify and address issues before the next health inspection.'
            })

        # Based on alerts
        critical_alerts = [a for a in alerts_data if a.get('severity') == 'CRITICAL']

        if critical_alerts:
            temp_alerts = [a for a in critical_alerts if 'temperature' in a.get('title', '').lower()]
            if temp_alerts:
                recommendations.append({
                    'category': 'Temperature Control',
                    'priority': 'High',
                    'title': 'Address Temperature Violations',
                    'description': f"{len(temp_alerts)} temperature alerts recorded. Review cooling, heating, and holding practices. Ensure all staff understand the danger zone (41°F - 135°F). Implement more frequent temperature monitoring log entries."
                })

        # Based on inspection history
        if inspection_history:
            latest = max(inspection_history, key=lambda x: x.get('inspection_date', datetime.min))
            violations = latest.get('violations', [])

            recurring_violations = self._find_recurring_violations(inspection_history)

            if recurring_violations:
                recommendations.append({
                    'category': 'Recurring Issues',
                    'priority': 'High',
                    'title': 'Fix Recurring Violation Pattern',
                    'description': f"Recurring issues detected: {', '.join(recurring_violations[:3])}. These violations appear across multiple inspections. Implement targeted training and process changes specifically for these areas to break the pattern."
                })

        # General best practices
        recommendations.append({
            'category': 'Best Practices',
            'priority': 'Medium',
            'title': 'Enhance Staff Training',
            'description': 'Schedule monthly food safety training sessions for all staff. Document training completion and keep records readily available for health department review.'
        })

        recommendations.append({
            'category': 'Monitoring',
            'priority': 'Low',
            'title': 'Increase Monitoring Frequency',
            'description': 'Add more automated sensors to areas with manual logging requirements. Automated continuous monitoring reduces human error and provides defensible data during inspections.'
        })

        return recommendations

    def _find_recurring_violations(self, inspection_history: List[Dict]) -> List[str]:
        """Find violations that appear in multiple inspections"""
        violation_counts = {}

        for inspection in inspection_history:
            for violation in inspection.get('violations', []):
                desc = violation.get('description', '')
                if desc:
                    # Simplify description to find patterns
                    key = desc.split('.')[0].strip().lower()
                    violation_counts[key] = violation_counts.get(key, 0) + 1

        # Return violations appearing 2+ times
        recurring = [v for v, count in violation_counts.items() if count >= 2]
        return sorted(recurring, key=lambda x: violation_counts[x], reverse=True)

    def _get_score_color(self, score):
        """Get color based on score"""
        if score >= 90:
            return colors.HexColor('#2E7D32')  # Green
        elif score >= 70:
            return colors.HexColor('#F9A825')  # Orange
        elif score >= 50:
            return colors.HexColor('#F57C00')  # Dark Orange
        else:
            return colors.HexColor('#C62828')  # Red


class InspectionPrepReportGenerator:
    """Generate inspection preparation reports"""

    def __init__(self):
        self._setup_styles()

    def _setup_styles(self):
        """Setup report styles"""
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='PrepTitle',
            parentName='Title',
            fontSize=20,
            textColor=colors.HexColor('#1565C0'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))

    def generate_prep_report(
        self,
        restaurant_data: Dict,
        inspection_prediction: Dict,
        risk_factors: List[str],
        checklist_items: List[Dict]
    ) -> bytes:
        """Generate inspection preparation checklist"""

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)

        story = []

        # Title
        story.append(Spacer(1*inch))
        story.append(Paragraph("Health Inspection Preparation Checklist", self.styles['PrepTitle']))
        story.append(Paragraph(
            f"Preparation Report for {restaurant_data.get('name', 'Restaurant')}",
            self.styles['Heading3']
        ))

        # Predicted inspection info
        predicted_date = inspection_prediction.get('predicted_date')
        predicted_score = inspection_prediction.get('predicted_score')
        confidence = inspection_prediction.get('confidence')

        story.append(Spacer(0.3*inch))

        pred_data = [
            ['Predicted Inspection Date', predicted_date.strftime('%B %d, %Y') if predicted_date else 'Unknown'],
            ['Predicted Score Range', f"{predicted_score - 10} - {predicted_score + 10}" if predicted_score else 'Unknown'],
            ['Confidence', f"{confidence:.0f}%" if confidence else 'N/A'],
            ['Last Inspection', inspection_prediction.get('last_inspection', 'N/A')],
        ]

        pred_table = Table(pred_data, colWidths=[2.5*inch, 2.5*inch])
        pred_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), (colors.white, colors.lightgrey)),
        ]))

        story.append(pred_table)
        story.append(Spacer(0.3*inch))

        # Risk factors
        story.append(Paragraph("Risk Factors to Address", self.styles['Heading2']))

        if risk_factors:
            for i, risk in enumerate(risk_factors, 1):
                story.append(Paragraph(
                    f"{i}. {risk}",
                    ParagraphStyle(
                        name='RiskFactor',
                        parentName='Normal',
                        fontSize=11,
                        leftIndent=20,
                        spaceAfter=8
                    )
                ))
        else:
            story.append(Paragraph("No significant risk factors identified.", self.styles['Normal']))

        # Checklist
        story.append(Spacer(0.2*inch))
        story.append(Paragraph("Pre-Inspection Checklist", self.styles['Heading2']))

        # Group by category
        categories = {}
        for item in checklist_items:
            category = item.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)

        for category, items in categories.items():
            story.append(Paragraph(category, self.styles['Heading3']))

            for i, item in enumerate(items, 1):
                checked = '☐'  # Empty checkbox
                story.append(Paragraph(
                    f"{checked} {item['task']}",
                    ParagraphStyle(
                        name='ChecklistItem',
                        parentName='Normal',
                        fontSize=10,
                        leftIndent=30,
                        spaceAfter=6
                    )
                ))

            story.append(Spacer(0.1*inch))

        # Tips section
        story.append(PageBreak())
        story.append(Paragraph("Tips for Inspection Success", self.styles['Heading2']))

        tips = [
            "Be present during the inspection to answer questions",
            "Have all monitoring logs readily available (last 30 days minimum)",
            "Ensure all staff are present and knowledgeable about food safety",
            "Clean all areas thoroughly before inspection",
            "Check that all equipment is functioning properly",
            "Have proof of employee food safety training available",
            "Review and fix any known issues before inspection",
            "Designate a knowledgeable staff member to accompany inspector",
        ]

        for i, tip in enumerate(tips, 1):
            story.append(Paragraph(
                f"{i}. {tip}",
                ParagraphStyle(
                    name='Tip',
                    parentName='Normal',
                    fontSize=11,
                    leftIndent=20,
                    spaceAfter=10
                )
            ))

        # Build PDF
        doc.build(story)
        return buffer.getvalue()


class ScorecardReportGenerator:
    """Generate simple scorecard reports"""

    def generate_scorecard(self, restaurant_data: Dict, metrics: Dict) -> bytes:
        """Generate one-page scorecard"""
        from reportlab.lib.enums import TA_CENTER

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20, bottomMargin=20)

        story = []

        # Header with score
        score = restaurant_data.get('compliance_score', 0)

        # Score circle would go here (simplified as text for now)
        story.append(Paragraph(
            f"{score:.0f}",
            ParagraphStyle(
                name='BigScore',
                parentName='Title',
                fontSize=144,
                textColor=self._get_score_color(score),
                alignment=TA_CENTER
            )
        ))

        story.append(Paragraph(
            "Compliance Score",
            ParagraphStyle(
                name='ScoreLabel',
                parentName='Heading2',
                fontSize=24,
                alignment=TA_CENTER,
                spaceAfter=30
            )
        ))

        # Metrics table
        metrics_data = [
            ['Metric', 'Value', 'Target'],
            ['Temperature Monitoring', f"{metrics.get('temp_monitoring', 0):.0f}%", '100%'],
            ['Manual Logs Completed', f"{metrics.get('manual_logs', 0)}", 'Daily'],
            ['Alert Response Time', f"{metrics.get('alert_response_time', 0):.1f} min", '<5 min'],
            ['Sensor Uptime', f"{metrics.get('sensor_uptime', 0):.1f}%", '>95%'],
            ['Staff Training', f"{metrics.get('training_complete', 0):.0f}%", '100%'],
        ]

        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ]))

        story.append(metrics_table)

        # Footer
        story.append(Spacer(1*inch))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
            ParagraphStyle(
                name='Footer',
                parentName='Normal',
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        ))

        doc.build(story)
        return buffer.getvalue()

    def _get_score_color(self, score):
        """Get color based on score"""
        if score >= 90:
            return colors.HexColor('#2E7D32')  # Green
        elif score >= 70:
            return colors.HexColor('#F9A825')  # Yellow
        else:
            return colors.HexColor('#C62828')  # Red
