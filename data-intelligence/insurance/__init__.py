"""
Insurance Data Products Module

Provides risk assessment APIs, portfolio monitoring, and
predictive claim analytics for insurance partnerships.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """Insurance risk categories"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RestaurantRiskProfile:
    """Complete risk profile for insurance underwriting"""
    restaurant_id: str
    restaurant_name: str
    location: Dict[str, str]

    # Risk scores (0-100)
    overall_risk_score: float
    food_safety_risk: float
    compliance_risk: float
    operational_risk: float

    # Risk category
    risk_category: RiskCategory

    # Predictive analytics
    claim_probability: float
    estimated_annual_claims: float
    recommended_premium_adjustment: float

    # Verification
    compliance_monitoring_active: bool
    monitoring_start_date: Optional[datetime]

    # Detail
    risk_factors: List[str]
    mitigation_recommendations: List[str]

    generated_at: datetime


class InsuranceRiskEngine:
    """Risk assessment engine for insurance underwriting"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.risk_weights = {
            'inspection_history': 0.35,
            'compliance_monitoring': 0.25,
            'operational_practices': 0.20,
            'historical_claims': 0.15,
            'location_factors': 0.05
        }

    async def assess_restaurant_risk(
        self,
        restaurant: Dict,
        inspection_data: Optional[List[Dict]] = None,
        operational_data: Optional[Dict] = None,
        claims_history: Optional[List[Dict]] = None
    ) -> RestaurantRiskProfile:
        """Assess restaurant risk for insurance underwriting"""

        # Calculate risk components
        inspection_risk = self._calculate_inspection_risk(inspection_data)
        monitoring_benefit = self._calculate_monitoring_benefit(operational_data)
        operational_risk = self._calculate_operational_risk(operational_data)
        claims_risk = self._calculate_claims_risk(claims_history)

        # Overall risk score (0-100, higher = riskier)
        overall_risk = (
            inspection_risk * self.risk_weights['inspection_history'] +
            (100 - monitoring_benefit) * self.risk_weights['compliance_monitoring'] +
            operational_risk * self.risk_weights['operational_practices'] +
            claims_risk * self.risk_weights['historical_claims']
        )

        # Determine category
        risk_category = self._determine_risk_category(overall_risk)

        # Predictive analytics
        claim_prob = self._calculate_claim_probability(overall_risk, monitoring_benefit)
        estimated_claims = self._estimate_annual_claims(overall_risk, restaurant)
        premium_adjustment = self._calculate_premium_adjustment(
            overall_risk,
            monitoring_benefit
        )

        # Risk factors and mitigations
        risk_factors = self._identify_risk_factors(
            inspection_data,
            operational_data
        )
        mitigations = self._generate_mitigation_recommendations(
            risk_factors,
            operational_data
        )

        return RestaurantRiskProfile(
            restaurant_id=restaurant.get('id', ''),
            restaurant_name=restaurant.get('name', ''),
            location={
                'city': restaurant.get('city', ''),
                'state': restaurant.get('state', ''),
                'address': restaurant.get('address', '')
            },
            overall_risk_score=round(overall_risk, 1),
            food_safety_risk=round(inspection_risk, 1),
            compliance_risk=round(100 - monitoring_benefit, 1),
            operational_risk=round(operational_risk, 1),
            risk_category=risk_category,
            claim_probability=round(claim_prob, 1),
            estimated_annual_claims=round(estimated_claims, 2),
            recommended_premium_adjustment=round(premium_adjustment, 1),
            compliance_monitoring_active=operational_data.get('monitoring_active', False) if operational_data else False,
            monitoring_start_date=operational_data.get('monitoring_start') if operational_data else None,
            risk_factors=risk_factors,
            mitigation_recommendations=mitigations,
            generated_at=datetime.now()
        )

    def _calculate_inspection_risk(self, inspection_data: Optional[List[Dict]]) -> float:
        """Calculate risk based on inspection history"""

        if not inspection_data:
            return 50.0  # Neutral

        latest = inspection_data[0]
        score = latest.get('score', 85)

        # Score to risk conversion
        if score >= 95:
            return 10.0
        elif score >= 90:
            return 25.0
        elif score >= 80:
            return 45.0
        elif score >= 70:
            return 70.0
        else:
            return 90.0

    def _calculate_monitoring_benefit(self, operational_data: Optional[Dict]) -> float:
        """Calculate benefit of compliance monitoring (0-100)"""

        if not operational_data:
            return 0.0

        # If using HealthGuard, significant risk reduction
        if operational_data.get('monitoring_active'):
            return 40.0  # 40 point risk reduction

        return 0.0

    def _calculate_operational_risk(self, operational_data: Optional[Dict]) -> float:
        """Calculate operational risk factors"""

        if not operational_data:
            return 50.0

        risk = 50.0

        # Adjust for restaurant type
        rest_type = operational_data.get('type', '').lower()
        if 'healthcare' in rest_type or 'school' in rest_type:
            risk -= 10  # Usually more stringent
        elif 'buffet' in rest_type:
            risk += 20  # Higher risk

        # Adjust for age
        years_open = operational_data.get('years_open', 5)
        if years_open < 1:
            risk += 15  # New business
        elif years_open > 10:
            risk -= 10  # Established

        return max(0, min(risk, 100))

    def _calculate_claims_risk(self, claims_history: Optional[List[Dict]]) -> float:
        """Calculate risk based on claims history"""

        if not claims_history:
            return 30.0  # Baseline

        # Simple model: adjust based on claim frequency and severity
        total_claims = len(claims_history)
        total_paid = sum(c.get('amount', 0) for c in claims_history)

        # Risk increases with claims
        risk = 30.0 + (total_claims * 10) + (total_paid / 1000)

        return min(risk, 100.0)

    def _determine_risk_category(self, risk_score: float) -> RiskCategory:
        """Determine risk category from score"""

        if risk_score < 25:
            return RiskCategory.LOW
        elif risk_score < 50:
            return RiskCategory.MEDIUM
        elif risk_score < 75:
            return RiskCategory.HIGH
        else:
            return RiskCategory.CRITICAL

    def _calculate_claim_probability(
        self,
        risk_score: float,
        monitoring_benefit: float
    ) -> float:
        """Calculate probability of claim in next 12 months"""

        # Base probability from risk score
        base_prob = risk_score / 100

        # Monitoring reduces claims
        if monitoring_benefit > 0:
            base_prob *= 0.6  # 40% reduction

        return round(base_prob * 100, 1)

    def _estimate_annual_claims(self, risk_score: float, restaurant: Dict) -> float:
        """Estimate annual claim cost"""

        # Average foodborne illness claim: $15,000
        # Base probability adjusted by risk
        probability = risk_score / 100

        # Claim frequency (0-3 claims/year)
        frequency = probability * 3

        # Average claim amount
        seats = restaurant.get('seats', 50)
        avg_claim = 10000 + (seats * 50)  # Scales with size

        return frequency * avg_claim

    def _calculate_premium_adjustment(
        self,
        risk_score: float,
        monitoring_benefit: float
    ) -> float:
        """Calculate recommended premium adjustment (%)"""

        adjustment = 0.0

        # Risk-based adjustment
        if risk_score < 25:
            adjustment -= 20  # 20% discount for low risk
        elif risk_score > 75:
            adjustment += 30  # 30% surcharge for high risk

        # Monitoring discount
        if monitoring_benefit > 0:
            adjustment -= 15  # 15% discount for monitoring

        return adjustment

    def _identify_risk_factors(
        self,
        inspection_data: Optional[List[Dict]],
        operational_data: Optional[Dict]
    ) -> List[str]:
        """Identify specific risk factors"""

        factors = []

        if inspection_data:
            latest = inspection_data[0]
            if latest.get('score', 100) < 80:
                factors.append("Below-average inspection scores")

            critical_violations = [
                v for v in latest.get('violations', [])
                if v.get('severity') == 'critical'
            ]
            if critical_violations:
                factors.append("Critical violations on record")

        if operational_data:
            if not operational_data.get('monitoring_active'):
                factors.append("No automated compliance monitoring")

        if not factors:
            factors.append("No significant risk factors identified")

        return factors

    def _generate_mitigation_recommendations(
        self,
        risk_factors: List[str],
        operational_data: Optional[Dict]
    ) -> List[str]:
        """Generate risk mitigation recommendations"""

        mitigations = []

        if not operational_data or not operational_data.get('monitoring_active'):
            mitigations.append("Implement automated compliance monitoring")

        if "Below-average inspection scores" in risk_factors:
            mitigations.append("Conduct staff retraining on food safety protocols")

        if "Critical violations on record" in risk_factors:
            mitigations.append("Establish proactive inspection preparation routine")

        mitigations.append("Maintain temperature monitoring logs")
        mitigations.append("Schedule quarterly compliance audits")

        return mitigations


class PortfolioMonitor:
    """Monitor restaurant portfolios for insurance companies"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.risk_engine = InsuranceRiskEngine()

    async def monitor_portfolio(
        self,
        restaurants: List[Dict],
        inspection_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict:
        """Generate portfolio risk report"""

        # Assess each restaurant
        risk_profiles = []

        for restaurant in restaurants:
            restaurant_id = restaurant.get('id', '')
            inspection_data = inspection_data_map.get(restaurant_id) if inspection_data_map else None

            profile = await self.risk_engine.assess_restaurant_risk(
                restaurant,
                inspection_data
            )

            risk_profiles.append(profile)

        # Calculate portfolio metrics
        total_restaurants = len(risk_profiles)
        total_exposure = sum(p.estimated_annual_claims for p in risk_profiles)

        category_counts = {}
        for profile in risk_profiles:
            cat = profile.risk_category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        avg_risk_score = sum(p.overall_risk_score for p in risk_profiles) / total_restaurants

        monitoring_count = sum(
            1 for p in risk_profiles
            if p.compliance_monitoring_active
        )

        return {
            'portfolio_summary': {
                'total_restaurants': total_restaurants,
                'total_exposure': round(total_exposure, 2),
                'average_risk_score': round(avg_risk_score, 1),
                'with_monitoring': monitoring_count,
                'monitoring_penetration': round((monitoring_count / total_restaurants) * 100, 1)
            },
            'risk_distribution': category_counts,
            'high_risk_accounts': [
                {
                    'restaurant': p.restaurant_name,
                    'risk_score': p.overall_risk_score,
                    'estimated_claims': p.estimated_annual_claims
                }
                for p in risk_profiles
                if p.risk_category in [RiskCategory.HIGH, RiskCategory.CRITICAL]
            ],
            'recommendations': self._generate_portfolio_recommendations(risk_profiles),
            'generated_at': datetime.now().isoformat()
        }

    def _generate_portfolio_recommendations(self, risk_profiles: List[RestaurantRiskProfile]) -> List[str]:
        """Generate portfolio-level recommendations"""

        recommendations = []

        monitoring_count = sum(
            1 for p in risk_profiles
            if p.compliance_monitoring_active
        )

        total = len(risk_profiles)

        if monitoring_count < total * 0.5:
            recommendations.append(
                f"Only {monitoring_count} of {total} accounts have compliance monitoring. "
                "Encourage adoption to reduce claims."
            )

        high_risk_count = sum(
            1 for p in risk_profiles
            if p.risk_category in [RiskCategory.HIGH, RiskCategory.CRITICAL]
        )

        if high_risk_count > total * 0.2:
            recommendations.append(
                f"{high_risk_count} accounts are high-risk. Consider targeted intervention."
            )

        recommendations.append("Review claims data quarterly to validate risk models")
        recommendations.append("Offer premium discounts for monitored accounts")

        return recommendations


__all__ = [
    'InsuranceRiskEngine',
    'PortfolioMonitor',
    'RestaurantRiskProfile',
    'RiskCategory'
]
