"""
Competitor Monitoring System

Detects competitor sensor installations, market penetration, and
competitive intelligence to inform sales strategy and market positioning.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class CompetitorType(Enum):
    """Types of competitors in the food safety monitoring space"""
    DIRECT_COMPETITOR = "direct"  # Similar IoT sensor systems
    INDIRECT_COMPETITOR = "indirect"  # Digital logging apps
    TRADITIONAL_COMPETITOR = "traditional"  # Paper/logging services
    CONSULTANT = "consultant"  # Food safety consultants


@dataclass
class CompetitorInstallation:
    """Detected competitor installation"""
    competitor_name: str
    competitor_type: CompetitorType
    restaurant_name: str
    address: str
    city: str
    state: str
    detection_method: str  # 'job_posting', 'review', 'photo', etc.
    confidence_score: float  # 0.0 to 1.0
    detection_date: datetime
    estimated_install_date: Optional[datetime]
    metadata: dict


@dataclass
class MarketIntelligence:
    """Market-level competitive intelligence"""
    state: str
    city: str
    zip_code: str

    # Market size
    total_restaurants: int
    competitor_penetration: float  # Percentage

    # Competitor breakdown
    competitor_market_shares: Dict[str, float]  # Competitor -> percentage

    # Opportunity analysis
    available_market: int  # Restaurants without monitoring
    market_saturation: str  # 'low', 'medium', 'high'

    last_updated: datetime


class CompetitorMonitor:
    """Monitors competitor activity and market penetration"""

    def __init__(self, config: dict):
        self.config = config
        self.competitors = self._load_competitors()
        self.detection_patterns = self._load_detection_patterns()

    def _load_competitors(self) -> Dict[str, dict]:
        """Load known competitors and their identifiers"""

        return {
            'SensorRich': {
                'type': CompetitorType.DIRECT_COMPETITOR,
                'keywords': ['sensorrich', 'sensor rich', 'senserrich'],
                'hardware_indicators': [
                    'small white sensors', 'temperature probes', 'gateway box'
                ],
                'job_keywords': ['SensorRich', 'deploying sensors', 'installation technician']
            },
            'ComplianceGuard': {
                'type': CompetitorType.DIRECT_COMPETITOR,
                'keywords': ['complianceguard', 'compliance guard', 'cg sensors'],
                'hardware_indicators': ['blue sensors', 'tablet dashboard'],
                'job_keywords': ['ComplianceGuard', 'sensor installation']
            },
            'TempTrack': {
                'type': CompetitorType.DIRECT_COMPETITOR,
                'keywords': ['temptrack', 'temp track'],
                'hardware_indicators': ['wireless temp sensors'],
                'job_keywords': ['TempTrack']
            },
            'SafeFoodPro': {
                'type': CompetitorType.INDIRECT_COMPETITOR,
                'keywords': ['safefoodpro', 'safe food pro'],
                'app_indicators': ['digital checklist', 'tablet inspection'],
                'job_keywords': ['SafeFoodPro', 'digital food safety']
            },
            'FoodLogiQ': {
                'type': CompetitorType.INDIRECT_COMPETITOR,
                'keywords': ['foodlogiq', 'food logiq'],
                'software_indicators': ['food safety software', 'digital log'],
                'job_keywords': ['FoodLogiQ']
            }
        }

    def _load_detection_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for detecting competitor installations"""

        return {
            'job_postings': [
                r'installing.*temperature.*sensor',
                r'deploy.*iot.*sensor',
                r'food.*safety.*monitoring.*system',
                r'compliance.*sensor.*installation'
            ],
            'reviews': [
                r'sensors.*monitor.*temperature',
                r'automated.*temperature.*logging',
                r'digital.*food.*safety',
                r'wireless.*sensor.*system'
            ],
            'photos': [
                # Would use image recognition in production
                'sensor_visible',
                'gateway_visible',
                'probe_visible'
            ]
        }

    async def detect_competitor_installations(
        self,
        territory: dict,  # {state, city, zip_codes}
        sources: List[str] = None
    ) -> List[CompetitorInstallation]:
        """
        Detect competitor installations in a territory

        Sources:
        - job_postings: Indeed, LinkedIn, etc.
        - reviews: Google, Yelp, etc.
        - photos: Social media images
        - business_licenses: Installation permits
        """

        if sources is None:
            sources = ['job_postings', 'reviews', 'business_licenses']

        installations = []

        # Check job postings for installation activity
        if 'job_postings' in sources:
            job_installations = await self._scan_job_postings(territory)
            installations.extend(job_installations)

        # Check reviews for mentions
        if 'reviews' in sources:
            review_installations = await self._scan_reviews(territory)
            installations.extend(review_installations)

        # Check business licenses/permits
        if 'business_licenses' in sources:
            permit_installations = await self._scan_permits(territory)
            installations.extend(permit_installations)

        logger.info(f"Detected {len(installations)} competitor installations in {territory.get('city', territory['state'])}")
        return installations

    async def _scan_job_postings(self, territory: dict) -> List[CompetitorInstallation]:
        """Scan job postings for installation activity"""

        # In production, query:
        # - Indeed API
        # - LinkedIn Jobs
        # - ZipRecruiter
        # - Glassdoor

        installations = []

        # Mock detection
        for competitor_name, competitor_info in self.competitors.items():
            # Search for competitor installation jobs in territory
            # In production: API call to job boards

            # Simulated detection
            pass

        return installations

    async def _scan_reviews(self, territory: dict) -> List[CompetitorInstallation]:
        """Scan reviews for competitor mentions"""

        # In production, query review platforms for competitor keywords

        installations = []

        for competitor_name, competitor_info in self.competitors.items():
            # Search for competitor keywords in reviews
            pass

        return installations

    async def _scan_permits(self, territory: dict) -> List[CompetitorInstallation]:
        """Scan business permits for installation approvals"""

        # Some cities require permits for sensor installations
        # Check local building department records

        return []

    async def calculate_market_penetration(
        self,
        territory: dict
    ) -> MarketIntelligence:
        """
        Calculate competitor market penetration in a territory

        Returns percentage of restaurants using monitoring solutions
        """

        # Get total restaurant count
        total_restaurants = await self._count_restaurants(territory)

        # Count competitor installations
        installations = await self.detect_competitor_installations(territory)

        # Count HealthGuard installations
        healthguard_count = await self._count_healthguard_installations(territory)

        # Calculate penetrations
        monitored_count = len(installations) + healthguard_count
        penetration_rate = (monitored_count / total_restaurants * 100) if total_restaurants > 0 else 0

        # Calculate market shares
        competitor_counts = {}
        for installation in installations:
            competitor_counts[installation.competitor_name] = \
                competitor_counts.get(installation.competitor_name, 0) + 1

        competitor_market_shares = {}
        if monitored_count > 0:
            for competitor, count in competitor_counts.items():
                competitor_market_shares[competitor] = (count / monitored_count * 100)

            if healthguard_count > 0:
                competitor_market_shares['HealthGuard'] = \
                    (healthguard_count / monitored_count * 100)

        # Determine saturation level
        if penetration_rate < 10:
            saturation = 'low'
        elif penetration_rate < 25:
            saturation = 'medium'
        else:
            saturation = 'high'

        intelligence = MarketIntelligence(
            state=territory['state'],
            city=territory.get('city', ''),
            zip_code=territory.get('zip_code', ''),
            total_restaurants=total_restaurants,
            competitor_penetration=penetration_rate,
            competitor_market_shares=competitor_market_shares,
            available_market=total_restaurants - monitored_count,
            market_saturation=saturation,
            last_updated=datetime.now()
        )

        return intelligence

    async def _count_restaurants(self, territory: dict) -> int:
        """Count total restaurants in territory"""

        # In production, query:
        # - Census data
        # - Business registries
        # - Yelp Fusion API
        # - Google Places API

        # Mock count
        return 2500

    async def _count_healthguard_installations(self, territory: dict) -> int:
        """Count existing HealthGuard installations"""

        # Query internal database
        # In production: SELECT COUNT(*) FROM restaurants WHERE territory = ?

        return 0

    def identify_competitive_vulnerability(
        self,
        intelligence: MarketIntelligence,
        restaurant: dict
    ) -> dict:
        """
        Identify competitive vulnerability for a specific restaurant

        Returns likelihood of displacing competitor
        """

        vulnerability_score = 0.0
        factors = []

        # Low market saturation = high opportunity
        if intelligence.market_saturation == 'low':
            vulnerability_score += 30
            factors.append({
                'factor': 'low_market_penetration',
                'impact': 30,
                'description': 'Low competitor penetration in market'
            })

        # Age of competitor installation (older = more vulnerable)
        # Would need installation date from detection
        vulnerability_score += 20
        factors.append({
            'factor': 'installation_age',
            'impact': 20,
            'description': 'Aging competitor installations vulnerable to replacement'
        })

        # Competitor reputation
        # Could analyze review sentiment for competitor
        vulnerability_score += 15
        factors.append({
            'factor': 'competitor_satisfaction',
            'impact': 15,
            'description': 'Mixed reviews for competitor solutions'
        })

        # Price sensitivity
        # Check if competitor pricing is high
        vulnerability_score += 15
        factors.append({
            'factor': 'price_competitiveness',
            'impact': 15,
            'description': 'HealthGuard pricing advantage'
        })

        # Feature advantage
        vulnerability_score += 20
        factors.append({
            'factor': 'feature_advantage',
            'impact': 20,
            'description': 'Superior offline capabilities and analytics'
        })

        return {
            'restaurant_name': restaurant.get('name'),
            'vulnerability_score': min(vulnerability_score, 100),
            'displacement_probability': 'high' if vulnerability_score > 70 else 'medium' if vulnerability_score > 40 else 'low',
            'factors': factors,
            'recommended_approach': self._recommend_approach(vulnerability_score)
        }

    def _recommend_approach(self, vulnerability_score: float) -> str:
        """Recommend sales approach based on vulnerability score"""

        if vulnerability_score > 70:
            return (
                "High vulnerability - Direct displacement strategy. "
                "Emphasize superior features, offline capability, and cost savings. "
                "Offer migration incentive."
            )
        elif vulnerability_score > 40:
            return (
                "Medium vulnerability - Comparative selling. "
                "Highlight feature advantages and ROI. "
                "Offer trial or pilot program."
            )
        else:
            return (
                "Low vulnerability - Differentiated positioning. "
                "Focus on unique value props: data intelligence, "
                "predictive analytics, industry expertise."
            )

    async def generate_competitive_intelligence_report(
        self,
        territories: List[dict]
    ) -> dict:
        """
        Generate comprehensive competitive intelligence report

        Includes:
        - Market penetration by territory
        - Competitor market shares
        - Vulnerable targets
        - Opportunity sizing
        """

        report = {
            'generated_at': datetime.now().isoformat(),
            'territories_analyzed': len(territories),
            'market_intelligence': [],
            'overall_competitor_position': {},
            'top_opportunity_territories': [],
            'recommendations': []
        }

        total_market_size = 0
        total_penetrated = 0
        competitor_totals = {}

        for territory in territories:
            intelligence = await self.calculate_market_penetration(territory)
            report['market_intelligence'].append({
                'territory': f"{intelligence.city}, {intelligence.state}" if intelligence.city else intelligence.state,
                'total_restaurants': intelligence.total_restaurants,
                'penetration_rate': intelligence.competitor_penetration,
                'market_saturation': intelligence.market_saturation,
                'available_market': intelligence.available_market,
                'competitor_shares': intelligence.competitor_market_shares
            })

            # Aggregate totals
            total_market_size += intelligence.total_restaurants
            total_penetrated += (intelligence.total_restaurants - intelligence.available_market)

            # Track competitor totals
            for competitor, share in intelligence.competitor_market_shares.items():
                competitor_totals[competitor] = competitor_totals.get(competitor, 0) + share

            # Track top opportunities
            if intelligence.market_saturation == 'low':
                report['top_opportunity_territories'].append({
                    'territory': f"{intelligence.city}, {intelligence.state}" if intelligence.city else intelligence.state,
                    'available_market': intelligence.available_market,
                    'opportunity_score': intelligence.available_market / intelligence.total_restaurants * 100
                })

        # Calculate overall position
        overall_penetration = (total_penetrated / total_market_size * 100) if total_market_size > 0 else 0

        report['overall_competitor_position'] = {
            'total_market_size': total_market_size,
            'total_penetrated': total_penetrated,
            'overall_penetration_rate': overall_penetration,
            'market_opportunity': total_market_size - total_penetrated,
            'competitor_aggregate_shares': competitor_totals
        }

        # Sort top opportunities
        report['top_opportunity_territories'].sort(
            key=lambda x: x['opportunity_score'],
            reverse=True
        )
        report['top_opportunity_territories'] = report['top_opportunity_territories'][:10]

        # Generate recommendations
        report['recommendations'] = self._generate_strategic_recommendations(report)

        return report

    def _generate_strategic_recommendations(self, report: dict) -> List[str]:
        """Generate strategic recommendations based on intelligence"""

        recommendations = []

        penetration = report['overall_competitor_position']['overall_penetration_rate']

        if penetration < 10:
            recommendations.append(
                "Market is largely untapped. Focus on awareness-building "
                "and first-mover advantage. Prioritize high-density urban areas."
            )
        elif penetration < 25:
            recommendations.append(
                "Market penetration is growing. Increase sales velocity "
                "and focus on competitor displacement in high-value territories."
            )
        else:
            recommendations.append(
                "Market is becoming saturated. Focus on premium positioning, "
                "enterprise sales, and adjacent markets."
            )

        # Competitor-specific recommendations
        competitor_shares = report['overall_competitor_position']['competitor_aggregate_shares']
        top_competitor = max(competitor_shares, key=competitor_shares.get) if competitor_shares else None

        if top_competitor:
            recommendations.append(
                f"Primary competitor is {top_competitor} with {competitor_shares[top_competitor]:.1f}% market share. "
                f"Develop targeted displacement strategy highlighting HealthGuard advantages."
            )

        return recommendations

    async def monitor_competitor_moves(
        self,
        territory: dict,
        alert_threshold: int = 5
    ) -> List[dict]:
        """
        Monitor for significant competitor moves in a territory

        Alerts when:
        - Sudden increase in installations (> threshold in 30 days)
        - New market entry
        - Price changes
        - Product launches
        """

        # Compare current installations to historical baseline
        current_installations = await self.detect_competitor_installations(territory)

        # In production, compare to baseline from 30 days ago
        baseline_count = 0  # Would fetch from database
        current_count = len(current_installations)

        alerts = []

        if current_count - baseline_count >= alert_threshold:
            alerts.append({
                'alert_type': 'competitor_expansion',
                'territory': f"{territory.get('city', territory['state'])}",
                'new_installations': current_count - baseline_count,
                'total_installations': current_count,
                'severity': 'high' if (current_count - baseline_count) >= 10 else 'medium',
                'recommended_action': 'Increase sales presence and marketing in territory'
            })

        return alerts
