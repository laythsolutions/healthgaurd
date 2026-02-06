"""
Real-Time Monitoring Engine

Continuously monitors public health data sources, social media, and
competitor activity to generate real-time alerts and intelligence updates.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RealTimeAlert:
    """Real-time alert from monitoring system"""
    alert_id: str
    alert_type: str
    severity: AlertSeverity
    restaurant_id: Optional[str]
    restaurant_name: str
    location: dict  # {city, state, address}

    # Alert details
    title: str
    description: str
    data: dict

    # Metadata
    detected_at: datetime
    source: str
    confidence: float  # 0.0 to 1.0

    # Actions
    action_required: bool
    recommended_actions: List[str]


class RealTimeMonitoringEngine:
    """
    Real-time monitoring system for health compliance intelligence

    Monitors:
    1. Public health inspection data updates
    2. Social media compliance mentions
    3. Competitor activity
    4. Business registry changes
    5. News and regulatory updates
    """

    def __init__(self, config: dict):
        self.config = config
        self.monitoring_active = False
        self.alert_handlers = []
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Monitoring intervals (in seconds)
        self.intervals = {
            'health_department': 3600,  # 1 hour
            'social_media': 1800,       # 30 minutes
            'competitor': 7200,         # 2 hours
            'business_registry': 86400, # 24 hours
            'news': 3600                # 1 hour
        }

        # Alert thresholds
        self.thresholds = {
            'score_drop': 5,           # 5-point inspection score drop
            'critical_violation': True,
            'food_illness_mentions': 1, # Any verified food illness mention
            'competitor_expansion': 5,   # 5+ new installations
            'license_change': True       # Any license/permit change
        }

    async def start_monitoring(
        self,
        territories: List[dict],
        alert_callback: Callable[[RealTimeAlert], None]
    ):
        """Start continuous monitoring loop"""

        self.monitoring_active = True
        self.alert_handlers.append(alert_callback)

        logger.info(f"Starting real-time monitoring for {len(territories)} territories")

        # Start monitoring tasks for each source
        tasks = [
            self._monitor_health_departments(territories),
            self._monitor_social_media(territories),
            self._monitor_competitors(territories),
            self._monitor_business_registries(territories),
            self._monitor_news(territories)
        ]

        # Run all monitoring tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_monitoring(self):
        """Stop all monitoring"""
        self.monitoring_active = False
        logger.info("Stopping real-time monitoring")

    async def _monitor_health_departments(self, territories: List[dict]):
        """Monitor public health department data for updates"""

        while self.monitoring_active:
            try:
                logger.info("Checking health department updates...")

                for territory in territories:
                    # Check for new inspection results
                    alerts = await self._check_new_inspections(territory)
                    for alert in alerts:
                        await self._dispatch_alert(alert)

                # Wait for next check
                await asyncio.sleep(self.intervals['health_department'])

            except Exception as e:
                logger.error(f"Error monitoring health departments: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

    async def _monitor_social_media(self, territories: List[dict]):
        """Monitor social media for compliance mentions"""

        while self.monitoring_active:
            try:
                logger.info("Checking social media for compliance mentions...")

                from ..harvesters.social_monitor import SocialReviewMonitor

                monitor = SocialReviewMonitor(self.config)

                for territory in territories:
                    # Get list of restaurants to monitor
                    restaurants = await self._get_restaurants_in_territory(territory)

                    # Check each restaurant
                    for restaurant in restaurants[:50]:  # Limit batch size
                        mentions = await monitor.monitor_restaurant_reviews(
                            restaurant_name=restaurant['name'],
                            address=restaurant['address'],
                            days_back=1  # Last 24 hours
                        )

                        # Generate alerts if needed
                        alert = await monitor.generate_compliance_alert(mentions)
                        if alert:
                            real_time_alert = self._convert_to_real_time_alert(
                                alert, 'social_media'
                            )
                            await self._dispatch_alert(real_time_alert)

                await asyncio.sleep(self.intervals['social_media'])

            except Exception as e:
                logger.error(f"Error monitoring social media: {e}")
                await asyncio.sleep(60)

    async def _monitor_competitors(self, territories: List[dict]):
        """Monitor competitor activity"""

        while self.monitoring_active:
            try:
                logger.info("Checking competitor activity...")

                from ..harvesters.competitor_monitor import CompetitorMonitor

                monitor = CompetitorMonitor(self.config)

                for territory in territories:
                    alerts = await monitor.monitor_competitor_moves(
                        territory,
                        alert_threshold=self.thresholds['competitor_expansion']
                    )

                    for alert in alerts:
                        real_time_alert = RealTimeAlert(
                            alert_id=f"comp-{datetime.now().timestamp()}",
                            alert_type='competitor_expansion',
                            severity=AlertSeverity.HIGH if alert['severity'] == 'high' else AlertSeverity.MEDIUM,
                            restaurant_id=None,
                            restaurant_name='N/A',
                            location={
                                'city': territory.get('city', ''),
                                'state': territory['state']
                            },
                            title=f"Competitor Expansion: {alert['territory']}",
                            description=f"{alert['new_installations']} new competitor installations detected",
                            data=alert,
                            detected_at=datetime.now(),
                            source='competitor_monitor',
                            confidence=0.8,
                            action_required=True,
                            recommended_actions=[alert['recommended_action']]
                        )
                        await self._dispatch_alert(real_time_alert)

                await asyncio.sleep(self.intervals['competitor'])

            except Exception as e:
                logger.error(f"Error monitoring competitors: {e}")
                await asyncio.sleep(60)

    async def _monitor_business_registries(self, territories: List[dict]):
        """Monitor business registries for changes"""

        while self.monitoring_active:
            try:
                logger.info("Checking business registry changes...")

                # Check for:
                # - New business registrations
                # - Business closures
                # - Ownership changes
                # - License/permit changes

                await asyncio.sleep(self.intervals['business_registry'])

            except Exception as e:
                logger.error(f"Error monitoring business registries: {e}")
                await asyncio.sleep(60)

    async def _monitor_news(self, territories: List[dict]):
        """Monitor news and regulatory updates"""

        while self.monitoring_active:
            try:
                logger.info("Checking news and regulatory updates...")

                # Check for:
                # - Food safety regulation changes
                # - Health department announcements
                # - Foodborne illness outbreaks
                # - Industry news

                await asyncio.sleep(self.intervals['news'])

            except Exception as e:
                logger.error(f"Error monitoring news: {e}")
                await asyncio.sleep(60)

    async def _check_new_inspections(self, territory: dict) -> List[RealTimeAlert]:
        """Check for new inspection results in territory"""

        alerts = []

        # In production, query health department API for new results
        # For now, simulate alert generation

        # Example: Score drop alert
        alerts.append(RealTimeAlert(
            alert_id=f"score-{datetime.now().timestamp()}",
            alert_type='inspection_score_drop',
            severity=AlertSeverity.HIGH,
            restaurant_id='rest_123',
            restaurant_name='Example Restaurant',
            location={
                'city': territory.get('city', ''),
                'state': territory['state']
            },
            title='Inspection Score Drop Detected',
            description='Inspection score dropped by 12 points (92 → 80)',
            data={
                'previous_score': 92,
                'current_score': 80,
                'drop_amount': 12,
                'inspection_date': datetime.now().isoformat(),
                'violations': ['Temperature control', 'Sanitization']
            },
            detected_at=datetime.now(),
            source='health_department',
            confidence=1.0,
            action_required=True,
            recommended_actions=[
                'Contact restaurant immediately',
                'Offer compliance consulting',
                'Update risk assessment',
                'Schedule follow-up monitoring'
            ]
        ))

        return alerts

    async def _get_restaurants_in_territory(self, territory: dict) -> List[dict]:
        """Get list of restaurants in territory"""

        # In production, query database
        # For now, return mock data
        return []

    def _convert_to_real_time_alert(self, social_alert: dict, source: str) -> RealTimeAlert:
        """Convert social media alert to real-time alert"""

        severity_map = {
            'critical': AlertSeverity.CRITICAL,
            'high': AlertSeverity.HIGH,
            'medium': AlertSeverity.MEDIUM,
            'low': AlertSeverity.LOW
        }

        return RealTimeAlert(
            alert_id=f"social-{datetime.now().timestamp()}",
            alert_type='social_media_compliance_risk',
            severity=severity_map.get(social_alert['severity'], AlertSeverity.MEDIUM),
            restaurant_id=None,
            restaurant_name=social_alert['restaurant_name'],
            location={
                'city': '',
                'state': ''
            },
            title='Social Media Compliance Risk Detected',
            description=social_alert.get('recommendation', ''),
            data=social_alert,
            detected_at=datetime.fromisoformat(social_alert['created_at']),
            source=source,
            confidence=0.7,
            action_required=social_alert['severity'] in ['critical', 'high'],
            recommended_actions=[social_alert.get('recommendation', '')]
        )

    async def _dispatch_alert(self, alert: RealTimeAlert):
        """Dispatch alert to all registered handlers"""

        logger.info(f"Dispatching alert: {alert.alert_type} - {alert.title}")

        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")

    async def generate_daily_summary(
        self,
        territories: List[dict]
    ) -> dict:
        """Generate daily monitoring summary"""

        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'territories_monitored': len(territories),
            'total_alerts': 0,
            'alerts_by_severity': {},
            'alerts_by_type': {},
            'top_alerts': [],
            'recommendations': []
        }

        # In production, query alerts from database for last 24 hours
        # For now, return template

        return summary


class AlertAggregator:
    """Aggregates and deduplicates alerts"""

    def __init__(self, dedup_window_minutes: int = 60):
        self.dedup_window = timedelta(minutes=dedup_window_minutes)
        self.recent_alerts = []

    def add_alert(self, alert: RealTimeAlert) -> Optional[RealTimeAlert]:
        """Add alert, return None if duplicate"""

        # Check for recent similar alerts
        for recent in self.recent_alerts:
            if self._is_duplicate(alert, recent):
                logger.info(f"Duplicate alert detected and filtered: {alert.alert_id}")
                return None

        # Add to recent alerts
        self.recent_alerts.append(alert)

        # Clean old alerts
        cutoff = datetime.now() - self.dedup_window
        self.recent_alerts = [
            a for a in self.recent_alerts
            if a.detected_at > cutoff
        ]

        return alert

    def _is_duplicate(self, alert1: RealTimeAlert, alert2: RealTimeAlert) -> bool:
        """Check if two alerts are duplicates"""

        # Same restaurant and alert type within window
        return (
            alert1.restaurant_name == alert2.restaurant_name and
            alert1.alert_type == alert2.alert_type and
            (alert1.detected_at - alert2.detected_at) < self.dedup_window
        )


class AlertPrioritizer:
    """Prioritizes alerts based on multiple factors"""

    def prioritize_alerts(self, alerts: List[RealTimeAlert]) -> List[RealTimeAlert]:
        """Sort alerts by priority"""

        def calculate_priority(alert: RealTimeAlert) -> float:
            score = 0.0

            # Severity (0-40 points)
            severity_scores = {
                AlertSeverity.CRITICAL: 40,
                AlertSeverity.HIGH: 30,
                AlertSeverity.MEDIUM: 20,
                AlertSeverity.LOW: 10,
                AlertSeverity.INFO: 0
            }
            score += severity_scores.get(alert.severity, 0)

            # Confidence (0-20 points)
            score += alert.confidence * 20

            # Recency (0-20 points) - more recent = higher priority
            hours_old = (datetime.now() - alert.detected_at).total_seconds() / 3600
            score += max(0, 20 - hours_old)

            # Action required (0-20 points)
            if alert.action_required:
                score += 20

            return score

        return sorted(alerts, key=calculate_priority, reverse=True)
