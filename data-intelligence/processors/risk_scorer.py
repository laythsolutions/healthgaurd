"""Risk scoring and analytics engine"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RiskScore:
    """Restaurant risk score"""
    restaurant_id: str
    overall_score: float  # 0-100
    inspection_risk: float
    violation_risk: float
    historical_risk: float
    financial_risk: float
    confidence: float
    factors: Dict[str, float]
    recommendations: List[str]


class RiskScoringEngine:
    """Calculate risk scores for restaurants"""

    def __init__(self):
        self.weight_config = {
            'inspection_score': 0.35,
            'violation_count': 0.25,
            'violation_severity': 0.20,
            'historical_trend': 0.10,
            'time_since_inspection': 0.10,
        }

    def calculate_risk_score(
        self,
        inspection_records: List[Dict],
        current_date: datetime = None
    ) -> RiskScore:
        """Calculate comprehensive risk score for a restaurant"""

        if current_date is None:
            current_date = datetime.now()

        if not inspection_records:
            return self._no_data_risk_score()

        # Extract latest inspection
        latest_inspection = max(inspection_records, key=lambda x: x.get('inspection_date', datetime.min))

        # Calculate component scores
        inspection_score = self._score_inspection_result(latest_inspection)
        violation_score = self._score_violations(inspection_records)
        historical_score = self._score_historical_trend(inspection_records)
        financial_score = self._score_financial_risk(inspection_records)
        recency_score = self._score_inspection_recency(latest_inspection, current_date)

        # Calculate weighted overall score
        overall_score = (
            inspection_score * self.weight_config['inspection_score'] +
            violation_score * self.weight_config['violation_count'] +
            historical_score * self.weight_config['historical_trend'] +
            recency_score * self.weight_config['time_since_inspection']
        )

        # Normalize to 0-100 (higher = more risky)
        overall_score = min(100, max(0, overall_score))

        # Generate recommendations
        recommendations = self._generate_recommendations(
            overall_score,
            inspection_score,
            violation_score,
            historical_score
        )

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(inspection_records)

        return RiskScore(
            restaurant_id=latest_inspection.get('restaurant_id', ''),
            overall_score=overall_score,
            inspection_risk=inspection_score,
            violation_risk=violation_score,
            historical_risk=historical_score,
            financial_risk=financial_score,
            confidence=confidence,
            factors={
                'inspection_score': inspection_score,
                'violation_score': violation_score,
                'historical_score': historical_score,
                'financial_score': financial_score,
                'recency_score': recency_score,
            },
            recommendations=recommendations
        )

    def _score_inspection_result(self, inspection: Dict) -> float:
        """Score based on inspection result (0-100, higher = more risk)"""
        score = inspection.get('score')

        if score is None:
            return 50.0  # Medium risk if no score

        # Convert score to risk (100 - score = risk)
        # Score 100 = 0 risk, Score 0 = 100 risk
        risk = 100 - score

        return min(100, max(0, risk))

    def _score_violations(self, inspections: List[Dict]) -> float:
        """Score based on violation count and severity"""
        total_violations = 0
        critical_violations = 0
        total_inspections = len(inspections)

        for inspection in inspections:
            violations = inspection.get('violations', [])
            total_violations += len(violations)

            for violation in violations:
                if violation.get('severity') == 'critical':
                    critical_violations += 1

        # Average violations per inspection
        avg_violations = total_violations / max(total_inspections, 1)

        # Calculate risk score
        # Base risk from average violations
        violation_risk = min(100, avg_violations * 10)

        # Boost for critical violations
        critical_multiplier = 1 + (critical_violations * 0.5)

        return min(100, violation_risk * critical_multiplier)

    def _score_historical_trend(self, inspections: List[Dict]) -> float:
        """Score based on historical trend (improving vs worsening)"""
        if len(inspections) < 2:
            return 50.0  # No trend data

        # Sort by date
        sorted_inspections = sorted(
            inspections,
            key=lambda x: x.get('inspection_date', datetime.min)
        )

        # Calculate trend (most recent vs oldest)
        oldest_score = sorted_inspections[0].get('score')
        newest_score = sorted_inspections[-1].get('score')

        if oldest_score is None or newest_score is None:
            return 50.0

        # Calculate change (negative = getting worse = higher risk)
        score_change = oldest_score - newest_score

        # Convert to risk score
        # Improving = lower risk, Worsening = higher risk
        trend_risk = 50 + score_change

        return min(100, max(0, trend_risk))

    def _score_financial_risk(self, inspections: List[Dict]) -> float:
        """Score based on potential financial impact"""
        # Count critical violations that lead to fines
        fine_violations = 0

        for inspection in inspections:
            violations = inspection.get('violations', [])
            for violation in violations:
                category = violation.get('category', '')
                severity = violation.get('severity', '')

                # Categories that typically lead to fines
                if severity == 'critical' or category in ['foodborne_illness', 'vermin', 'sewage']:
                    fine_violations += 1

        # Estimate fine risk
        # Each critical violation = ~$500-1000 potential fine
        estimated_fine_risk = fine_violations * 500

        # Convert to 0-100 scale
        # $5000+ in potential fines = high risk
        fine_risk_score = min(100, estimated_fine_risk / 50)

        return fine_risk_score

    def _score_inspection_recency(self, inspection: Dict, current_date: datetime) -> float:
        """Score based on time since last inspection"""
        inspection_date = inspection.get('inspection_date')

        if not inspection_date:
            return 50.0

        if isinstance(inspection_date, str):
            inspection_date = datetime.fromisoformat(inspection_date)

        days_since = (current_date - inspection_date).days

        # Most jurisdictions inspect every 6-12 months
        # Overdue = higher risk
        if days_since > 365:
            return 100.0  # Very high risk - way overdue
        elif days_since > 180:
            return 75.0  # High risk - inspection due soon
        elif days_since > 90:
            return 50.0  # Medium risk
        else:
            return 25.0  # Low risk - recently inspected

    def _generate_recommendations(
        self,
        overall_score: float,
        inspection_score: float,
        violation_score: float,
        historical_score: float
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if overall_score > 70:
            recommendations.append("URGENT: Critical compliance issues detected")
            recommendations.append("Schedule professional food safety training immediately")

        if inspection_score > 60:
            recommendations.append("Review recent inspection violations with staff")
            recommendations.append("Implement corrective action plans for all critical items")

        if violation_score > 50:
            recommendations.append("Increase self-inspection frequency to daily")
            recommendations.append("Assign compliance champions for each shift")

        if historical_score > 60:
            recommendations.append("Trend worsening - intervention needed")
            recommendations.append("Consider third-party food safety audit")

        if overall_score < 30:
            recommendations.append("Good compliance standing - maintain current practices")
            recommendations.append("Prepare for upcoming health inspection")

        return recommendations

    def _calculate_confidence(self, inspections: List[Dict]) -> float:
        """Calculate confidence in risk score based on data quality"""
        if not inspections:
            return 0.0

        # More inspections = higher confidence
        inspection_count = len(inspections)

        # Recency of data
        latest_date = max(
            i.get('inspection_date', datetime.min)
            for i in inspections
        )

        if isinstance(latest_date, str):
            latest_date = datetime.fromisoformat(latest_date)

        days_since_latest = (datetime.now() - latest_date).days

        # Calculate confidence (0-100)
        count_score = min(100, inspection_count * 10)  # 10+ inspections = 100
        recency_score = max(0, 100 - days_since_latest)  # Decreases over time

        confidence = (count_score + recency_score) / 2

        return min(100, max(0, confidence))

    def _no_data_risk_score(self) -> RiskScore:
        """Return default risk score when no data available"""
        return RiskScore(
            restaurant_id='',
            overall_score=50.0,  # Medium risk when unknown
            inspection_risk=50.0,
            violation_risk=50.0,
            historical_risk=50.0,
            financial_risk=50.0,
            confidence=0.0,
            factors={},
            recommendations=[
                "No inspection data available - unknown risk level",
                "Consider manual inspection or research",
            ]
        )


class LeadScoringEngine:
    """Score restaurants for sales targeting"""

    def __init__(self):
        self.risk_engine = RiskScoringEngine()

    def calculate_lead_score(
        self,
        restaurant_data: Dict,
        public_inspection_data: List[Dict] = None
    ) -> Dict:
        """Calculate lead score for sales targeting"""

        scores = {}

        # 1. Health Guard Risk Score (40%)
        if public_inspection_data:
            risk_score = self.risk_engine.calculate_risk_score(public_inspection_data)
            healthguard_risk = risk_score.overall_score
        else:
            healthguard_risk = 50.0

        # 2. Restaurant Size (15%)
        seating_capacity = restaurant_data.get('seating_capacity', 0)
        size_score = min(100, seating_capacity / 2)  # 200+ seats = 100

        # 3. Cuisine Type Risk (10%)
        cuisine_type = restaurant_data.get('cuisine_type', '').lower()
        cuisine_risk = self._get_cuisine_risk(cuisine_type)

        # 4. Location Density (15%)
        city = restaurant_data.get('city', '')
        location_score = self._get_location_density(city)

        # 5. Competitive Gap (10%)
        has_competitor = restaurant_data.get('has_monitoring_system', False)
        competitor_gap = 100 if not has_competitor else 20

        # 6. Technology Readiness (10%)
        tech_score = self._estimate_tech_readiness(restaurant_data)

        # Calculate weighted lead score
        lead_score = (
            healthguard_risk * 0.40 +
            size_score * 0.15 +
            cuisine_risk * 0.10 +
            location_score * 0.15 +
            competitor_gap * 0.10 +
            tech_score * 0.10
        )

        # Determine acquisition probability
        acquisition_prob = self._estimate_acquisition_probability(
            lead_score,
            healthguard_risk,
            competitor_gap
        )

        # Calculate optimal contact timing
        timing = self._calculate_optimal_timing(
            healthguard_risk,
            public_inspection_data
        )

        return {
            'lead_score': lead_score,
            'acquisition_probability': acquisition_prob,
            'optimal_timing': timing,
            'healthguard_risk': healthguard_risk,
            'size_score': size_score,
            'competitor_gap': competitor_gap,
            'recommended_approach': self._get_approach(lead_score, competitor_gap),
            'talking_points': self._generate_talking_points(healthguard_risk),
        }

    def _get_cuisine_risk(self, cuisine: str) -> float:
        """Get risk score based on cuisine type"""
        high_risk_cuisines = ['sushi', 'buffet', 'raw bar', 'tapas']
        medium_risk_cuisines = ['american', 'italian', 'chinese', 'mexican']

        if any(risk in cuisine for risk in high_risk_cuisines):
            return 80.0
        elif any(risk in cuisine for risk in medium_risk_cuisines):
            return 60.0
        else:
            return 40.0

    def _get_location_density(self, city: str) -> float:
        """Get restaurant density score for city"""
        # Major metros = higher density
        major_cities = [
            'new york', 'los angeles', 'chicago', 'houston', 'phoenix',
            'philadelphia', 'san antonio', 'san diego', 'dallas', 'san jose'
        ]

        if city.lower() in major_cities:
            return 90.0
        else:
            return 50.0

    def _estimate_tech_readiness(self, data: Dict) -> float:
        """Estimate technology readiness"""
        score = 50.0  # Base score

        if data.get('online_ordering'):
            score += 20
        if data.get('pos_system'):
            score += 15
        if data.get('website'):
            score += 10
        if data.get('social_media'):
            score += 5

        return min(100, score)

    def _estimate_acquisition_probability(
        self,
        lead_score: float,
        healthguard_risk: float,
        competitor_gap: float
    ) -> float:
        """Estimate probability of closing the deal"""
        # High risk + no competitor = high probability
        base_prob = (healthguard_risk * 0.6 + competitor_gap * 0.4)

        # Adjust based on overall lead score
        if lead_score > 70:
            return min(90, base_prob * 1.2)
        elif lead_score > 50:
            return base_prob
        else:
            return max(10, base_prob * 0.7)

    def _calculate_optimal_timing(
        self,
        healthguard_risk: float,
        inspection_data: List[Dict] = None
    ) -> Dict:
        """Calculate optimal contact timing"""
        urgency = 'medium'
        days_to_contact = 7

        if healthguard_risk > 70:
            urgency = 'critical'
            days_to_contact = 1
        elif healthguard_risk > 50:
            urgency = 'high'
            days_to_contact = 3

        # Check if inspection due soon
        if inspection_data:
            latest = max(inspection_data, key=lambda x: x.get('inspection_date', datetime.min))
            days_since = (datetime.now() - latest.get('inspection_date', datetime.now())).days

            if days_since > 300:  # Inspection coming up
                days_to_contact = min(days_to_contact, 2)

        return {
            'urgency': urgency,
            'optimal_days': days_to_contact,
        }

    def _get_approach(self, lead_score: float, competitor_gap: float) -> str:
        """Get recommended sales approach"""
        if lead_score > 70:
            return 'direct_outreach'  # Call immediately
        elif lead_score > 50:
            return 'email_sequence'  # Start with email
        else:
            return 'nurture_campaign'  # Add to drip campaign

    def _generate_talking_points(self, healthguard_risk: float) -> List[str]:
        """Generate sales talking points based on risk"""
        points = []

        if healthguard_risk > 70:
            points.append("Recent inspection score below 70 - critical risk")
            points.append("Average fine for violations: $500-2000")
            points.append("Insurance premium increase: 15-25%")
        elif healthguard_risk > 40:
            points.append("Room for improvement in compliance")
            points.append("Prevent future violations")
        else:
            points.append("Maintain excellent compliance record")
            points.append("Demonstrate commitment to food safety")

        points.append("95% of our customers maintain 90+ inspection scores")
        points.append("Typical ROI: 10x investment in first year")

        return points
