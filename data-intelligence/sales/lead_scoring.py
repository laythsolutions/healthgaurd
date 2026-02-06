"""
Advanced Lead Scoring System

AI-powered lead scoring with 6-factor model for identifying
high-value restaurant targets for HealthGuard sales.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LeadTier(Enum):
    """Lead qualification tiers"""
    HOT = "hot"           # >80 points, contact immediately
    WARM = "warm"         # 60-79 points, contact within 48 hours
    COLD = "cold"         # 40-59 points, nurture campaign
    UNQUALIFIED = "unqualified"  # <40 points, do not pursue


@dataclass
class LeadScore:
    """Comprehensive lead scoring result"""
    restaurant_id: str
    restaurant_name: str
    overall_score: float  # 0-100
    tier: LeadTier

    # Component scores (0-100 each)
    health_risk_score: float
    acquisition_probability: float
    customer_lifetime_value: float
    strategic_value: float
    urgency_score: float
    competitive_vulnerability: float

    # Details
    factors: Dict[str, float]
    talking_points: List[str]
    recommended_approach: str

    # Optimal timing
    optimal_contact_date: datetime
    optimal_contact_time: str
    urgency: str

    # Objection handling
    likely_objections: List[str]
    objection_handlers: Dict[str, str]

    calculated_at: datetime


class AdvancedLeadScoringEngine:
    """
    Advanced 6-factor lead scoring model

    Factors:
    1. Health Risk Score (40%) - Inspection scores, violations, patterns
    2. Acquisition Probability (20%) - Market conditions, competition
    3. Customer Lifetime Value (15%) - Revenue potential, tenure
    4. Strategic Value (10%) - Chain relationship, market position
    5. Urgency Score (10%) - Recent violations, upcoming inspections
    6. Competitive Vulnerability (5%) - Displacement opportunity
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.weights = {
            'health_risk': 0.40,
            'acquisition_probability': 0.20,
            'clv': 0.15,
            'strategic_value': 0.10,
            'urgency': 0.10,
            'competitive_vulnerability': 0.05
        }

    async def score_lead(
        self,
        restaurant: Dict,
        inspection_data: Optional[List[Dict]] = None,
        market_intelligence: Optional[Dict] = None,
        competitor_data: Optional[Dict] = None
    ) -> LeadScore:
        """Calculate comprehensive lead score"""

        # Calculate component scores
        health_risk = self._calculate_health_risk_score(inspection_data or [])
        acquisition_prob = self._calculate_acquisition_probability(restaurant, market_intelligence)
        clv = self._calculate_customer_lifetime_value(restaurant)
        strategic = self._calculate_strategic_value(restaurant)
        urgency = self._calculate_urgency_score(inspection_data or [])
        competitive = self._calculate_competitive_vulnerability(competitor_data)

        # Weighted overall score
        overall_score = (
            health_risk * self.weights['health_risk'] +
            acquisition_prob * self.weights['acquisition_probability'] +
            clv * self.weights['clv'] +
            strategic * self.weights['strategic_value'] +
            urgency * self.weights['urgency'] +
            competitive * self.weights['competitive_vulnerability']
        )

        # Determine tier
        tier = self._determine_tier(overall_score)

        # Generate insights
        talking_points = self._generate_talking_points(
            health_risk, acquisition_prob, clv, urgency
        )
        approach = self._determine_approach(tier, health_risk, urgency)
        objections = self._predict_objections(restaurant)
        handlers = self._generate_objection_handlers(objections)

        # Optimal timing
        contact_date, contact_time, urgency_level = self._calculate_optimal_timing(
            restaurant, inspection_data, urgency
        )

        return LeadScore(
            restaurant_id=restaurant.get('id', ''),
            restaurant_name=restaurant.get('name', ''),
            overall_score=round(overall_score, 1),
            tier=tier,
            health_risk_score=round(health_risk, 1),
            acquisition_probability=round(acquisition_prob, 1),
            customer_lifetime_value=round(clv, 1),
            strategic_value=round(strategic, 1),
            urgency_score=round(urgency, 1),
            competitive_vulnerability=round(competitive, 1),
            factors={
                'health_risk': health_risk,
                'acquisition_probability': acquisition_prob,
                'clv': clv,
                'strategic_value': strategic,
                'urgency': urgency,
                'competitive_vulnerability': competitive
            },
            talking_points=talking_points,
            recommended_approach=approach,
            optimal_contact_date=contact_date,
            optimal_contact_time=contact_time,
            urgency=urgency_level,
            likely_objections=objections,
            objection_handlers=handlers,
            calculated_at=datetime.now()
        )

    def _calculate_health_risk_score(self, inspection_data: List[Dict]) -> float:
        """Calculate health risk score (0-100)"""

        if not inspection_data:
            return 50.0  # Neutral score

        latest_inspection = inspection_data[0]  # Most recent
        score = latest_inspection.get('score', 85)

        # Score to risk conversion (lower score = higher risk)
        if score >= 90:
            risk_score = 20.0  # Low risk
        elif score >= 80:
            risk_score = 40.0
        elif score >= 70:
            risk_score = 60.0
        elif score >= 60:
            risk_score = 80.0
        else:
            risk_score = 95.0  # Critical risk

        # Adjust for violations
        violation_count = len(latest_inspection.get('violations', []))
        risk_score += min(violation_count * 5, 20)

        # Check for critical violations
        critical_violations = [
            v for v in latest_inspection.get('violations', [])
            if v.get('severity') == 'critical'
        ]
        if critical_violations:
            risk_score += 15

        # Check trend
        if len(inspection_data) >= 2:
            prev_score = inspection_data[1].get('score', score)
            if score < prev_score:
                risk_score += 10  # Declining performance

        return min(risk_score, 100.0)

    def _calculate_acquisition_probability(
        self,
        restaurant: Dict,
        market_intelligence: Optional[Dict]
    ) -> float:
        """Calculate probability of successful acquisition (0-100)"""

        probability = 50.0  # Base probability

        # Restaurant type
        rest_type = restaurant.get('type', '').lower()
        if 'full service' in rest_type or 'fine dining' in rest_type:
            probability += 15  # Higher need for compliance
        elif 'fast food' in rest_type or 'quick service' in rest_type:
            probability += 10
        elif 'bakery' in rest_type or 'cafe' in rest_type:
            probability += 5

        # Size (revenue proxy)
        seats = restaurant.get('seats', 0)
        if seats > 150:
            probability += 15  # Larger operations have more to lose
        elif seats > 75:
            probability += 10
        elif seats > 30:
            probability += 5

        # Current compliance method
        current_method = restaurant.get('compliance_method', '')
        if current_method == 'manual':
            probability += 20  # Manual = high pain point
        elif current_method == 'competitor':
            probability -= 10  # Harder to displace

        # Market conditions
        if market_intelligence:
            penetration = market_intelligence.get('competitor_penetration', 0)
            if penetration < 10:
                probability += 10  # Untapped market
            elif penetration > 50:
                probability -= 10  # Saturated market

        # Ownership
        ownership = restaurant.get('ownership', '')
        if 'corporate' in ownership.lower() or 'chain' in ownership.lower():
            probability += 10  # Easier to sell to corporate

        return min(probability, 100.0)

    def _calculate_customer_lifetime_value(self, restaurant: Dict) -> float:
        """Calculate customer lifetime value score (0-100)"""

        # Estimate monthly revenue potential
        base_subscription = 150  # Average $150/month

        # Adjust by size
        seats = restaurant.get('seats', 50)
        size_multiplier = 1.0

        if seats > 200:
            size_multiplier = 2.0  # Premium pricing
        elif seats > 100:
            size_multiplier = 1.5

        estimated_monthly = base_subscription * size_multiplier

        # Add hardware upsell potential
        estimated_hardware = 500  # Sensor kit
        estimated_sensors = max(5, seats // 20)  # 1 sensor per 20 seats
        hardware_value = estimated_hardware + (estimated_sensors * 50)

        # 3-year LTV (industry standard)
        months = 36
        ltv = (estimated_monthly * months) + hardware_value

        # Convert to 0-100 scale ($0 = 0, $10,000 = 100)
        score = min((ltv / 10000) * 100, 100.0)

        return score

    def _calculate_strategic_value(self, restaurant: Dict) -> float:
        """Calculate strategic value (0-100)"""

        strategic_score = 0.0

        # Chain/franchise indicator
        name = restaurant.get('name', '').lower()
        if any(word in name for word in ['chain', 'franchise', 'group']):
            strategic_score += 30  # Multi-location potential

        # Location in major metro
        city = restaurant.get('city', '').lower()
        major_metros = [
            'new york', 'los angeles', 'chicago', 'houston', 'phoenix',
            'philadelphia', 'san antonio', 'san diego', 'dallas', 'san jose'
        ]
        if any(metro in city for metro in major_metros):
            strategic_score += 20  # High visibility market

        # Industry influence
        awards = restaurant.get('awards', [])
        if awards:
            strategic_score += 15  # Reference customer potential

        # Review volume (social influence)
        review_count = restaurant.get('review_count', 0)
        if review_count > 1000:
            strategic_score += 20
        elif review_count > 500:
            strategic_score += 10

        return min(strategic_score, 100.0)

    def _calculate_urgency_score(self, inspection_data: List[Dict]) -> float:
        """Calculate urgency score (0-100)"""

        if not inspection_data:
            return 30.0  # Low urgency

        latest = inspection_data[0]
        urgency = 0.0

        # Recent critical violation
        critical_violations = [
            v for v in latest.get('violations', [])
            if v.get('severity') == 'critical'
        ]
        if critical_violations:
            urgency += 40

        # Low score
        score = latest.get('score', 100)
        if score < 70:
            urgency += 30
        elif score < 80:
            urgency += 15

        # Recent inspection date (potential follow-up)
        inspection_date = latest.get('inspection_date')
        if inspection_date:
            days_since = (datetime.now() - datetime.fromisoformat(inspection_date)).days
            if days_since < 30:
                urgency += 20  # Still in correction window
            elif days_since < 90:
                urgency += 10

        # Violation trend
        if len(inspection_data) >= 2:
            prev_violations = len(inspection_data[1].get('violations', []))
            curr_violations = len(latest.get('violations', []))
            if curr_violations > prev_violations:
                urgency += 10  # Getting worse

        return min(urgency, 100.0)

    def _calculate_competitive_vulnerability(
        self,
        competitor_data: Optional[Dict]
    ) -> float:
        """Calculate competitive vulnerability (0-100)"""

        if not competitor_data:
            return 30.0  # Neutral

        vulnerability = 0.0

        # Has competitor installation
        if competitor_data.get('has_competitor'):
            # Competitor satisfaction
            satisfaction = competitor_data.get('competitor_satisfaction', 0.7)
            if satisfaction < 0.5:
                vulnerability += 40  # Unhappy customers

            # Installation age
            install_date = competitor_data.get('installation_date')
            if install_date:
                years_old = (datetime.now() - datetime.fromisoformat(install_date)).days / 365
                if years_old > 3:
                    vulnerability += 30  # Aging equipment
                elif years_old > 2:
                    vulnerability += 15

            # Feature gaps
            missing_features = competitor_data.get('missing_features', [])
            if 'offline_capability' in missing_features:
                vulnerability += 20
            if 'predictive_analytics' in missing_features:
                vulnerability += 10

        return min(vulnerability, 100.0)

    def _determine_tier(self, score: float) -> LeadTier:
        """Determine lead tier from score"""
        if score >= 80:
            return LeadTier.HOT
        elif score >= 60:
            return LeadTier.WARM
        elif score >= 40:
            return LeadTier.COLD
        else:
            return LeadTier.UNQUALIFIED

    def _generate_talking_points(
        self,
        health_risk: float,
        acquisition_prob: float,
        clv: float,
        urgency: float
    ) -> List[str]:
        """Generate personalized talking points"""

        points = []

        # Health risk talking points
        if health_risk > 70:
            points.append("Your recent inspection scores indicate significant compliance risk")
        elif health_risk > 50:
            points.append("There's room to improve your inspection consistency")

        # CLV talking points
        if clv > 70:
            points.append("Our enterprise-grade solution fits your scale perfectly")
        elif clv > 40:
            points.append("Affordable solution with strong ROI for your operation")

        # Urgency talking points
        if urgency > 70:
            points.append("Act now to prevent potential violations and fines")

        # Add differentiator
        points.append("Only system that works during internet outages")
        points.append("Predictive analytics tell you when inspections are coming")

        return points[:5]  # Top 5

    def _determine_approach(
        self,
        tier: LeadTier,
        health_risk: float,
        urgency: float
    ) -> str:
        """Determine recommended sales approach"""

        if tier == LeadTier.HOT:
            if health_risk > 70:
                return "direct_outreach"
            return "urgent_demo"

        elif tier == LeadTier.WARM:
            if health_risk > 50:
                return "consultative_selling"
            return "educational_approach"

        elif tier == LeadTier.COLD:
            return "nurture_campaign"

        else:
            return "do_not_pursue"

    def _predict_objections(self, restaurant: Dict) -> List[str]:
        """Predict likely objections"""

        objections = []

        # Price objection (common)
        objections.append("price_too_high")

        # Value objection
        objections.append("current_method_works")

        # Timing objection
        objections.append("not_right_time")

        # Trust objection
        objections.append("new_unknown_vendor")

        # Implementation objection
        objections.append("implementation_complexity")

        return objections

    def _generate_objection_handlers(self, objections: List[str]) -> Dict[str, str]:
        """Generate objection handlers"""

        handlers = {
            "price_too_high": (
                "I understand budget is a concern. The average restaurant sees $1,500+ in "
                "annual fine reduction alone. Our customers typically break even in 3-4 months. "
                "Would you like me to calculate your specific ROI?"
            ),
            "current_method_works": (
                "That's great that you have a system. However, our customers typically find "
                "that automation catches 40% more issues than manual logging, and our predictive "
                "analytics prevent violations before they happen. Can I show you the difference?"
            ),
            "not_right_time": (
                "I appreciate that. However, health inspections don't wait for convenient timing. "
                "Our system can be installed in under 2 hours and starts protecting you immediately. "
                "When would be a better time to ensure you're protected?"
            ),
            "new_unknown_vendor": (
                "That's a valid concern. We're currently protecting over 500 restaurants with "
                "99.7% uptime. I can provide references from similar restaurants in your area. "
                "Would you like to speak with one of our customers?"
            ),
            "implementation_complexity": (
                "Actually, it's very simple. We handle the entire installation - sensors, gateway, "
                "setup. Your staff just needs a 15-minute training session. Most restaurants are "
                "fully operational within 24 hours. When could we schedule the installation?"
            )
        }

        return handlers

    def _calculate_optimal_timing(
        self,
        restaurant: Dict,
        inspection_data: List[Dict],
        urgency: float
    ) -> tuple:
        """Calculate optimal contact timing"""

        # Urgent leads = contact immediately
        if urgency > 70:
            return (
                datetime.now(),
                "morning",  # Morning = more likely to reach decision maker
                "immediate"
            )

        # Check for inspection timing
        if inspection_data:
            latest = inspection_data[0]
            inspection_date = latest.get('inspection_date')
            if inspection_date:
                # Contact 2 weeks after inspection (results processed)
                contact_date = datetime.fromisoformat(inspection_date) + timedelta(days=14)
                if contact_date > datetime.now():
                    return (
                        contact_date,
                        "morning",
                        "upcoming_inspection"
                    )

        # Default timing
        return (
            datetime.now() + timedelta(days=3),
            "tuesday_morning",  # Best day for B2B calls
            "standard"
        )


class LeadBatchProcessor:
    """Process multiple leads in batch"""

    def __init__(self):
        self.engine = AdvancedLeadScoringEngine()

    async def score_batch(
        self,
        restaurants: List[Dict],
        inspection_data_map: Dict[str, List[Dict]] = None,
        market_intelligence: Dict = None,
        competitor_data_map: Dict[str, Dict] = None
    ) -> List[LeadScore]:
        """Score multiple leads in batch"""

        results = []

        for restaurant in restaurants:
            restaurant_id = restaurant.get('id', '')
            inspection_data = inspection_data_map.get(restaurant_id) if inspection_data_map else None
            competitor_data = competitor_data_map.get(restaurant_id) if competitor_data_map else None

            score = await self.engine.score_lead(
                restaurant,
                inspection_data,
                market_intelligence,
                competitor_data
            )

            results.append(score)

        # Sort by overall score
        results.sort(key=lambda x: x.overall_score, reverse=True)

        return results

    def prioritize_territory(
        self,
        scored_leads: List[LeadScore]
    ) -> Dict[str, List[LeadScore]]:
        """Prioritize leads by tier"""

        prioritized = {
            'hot': [],
            'warm': [],
            'cold': [],
            'unqualified': []
        }

        for lead in scored_leads:
            tier = lead.tier.value
            prioritized[tier].append(lead)

        return prioritized
