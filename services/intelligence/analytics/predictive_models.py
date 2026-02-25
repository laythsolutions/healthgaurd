"""Predictive analytics and ML models"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class InspectionPrediction:
    """Predicted health inspection outcome"""
    predicted_date: datetime
    predicted_score: int
    confidence: float
    risk_factors: List[str]
    recommendations: List[str]


class PredictiveAnalyticsEngine:
    """ML-powered predictive analytics"""

    def __init__(self):
        self.model_config = {
            'inspection_interval_days': 180,  # Average 6 months
            'score_std_dev': 15,  # Typical score variation
        }

    def predict_next_inspection(
        self,
        inspection_history: List[Dict],
        current_date: datetime = None
    ) -> InspectionPrediction:
        """Predict when next health inspection will occur"""

        if current_date is None:
            current_date = datetime.now()

        if not inspection_history:
            # No history - use average
            next_date = current_date + timedelta(days=self.model_config['inspection_interval_days'])
            return InspectionPrediction(
                predicted_date=next_date,
                predicted_score=75,  # Average score
                confidence=20.0,
                risk_factors=['No historical data available'],
                recommendations=['Gather inspection history from health department']
            )

        # Sort by date
        sorted_inspections = sorted(
            inspection_history,
            key=lambda x: self.get_date(x.get('inspection_date'))
        )

        # Calculate average interval
        if len(sorted_inspections) >= 2:
            intervals = []
            for i in range(1, len(sorted_inspections)):
                days = (
                    self.get_date(sorted_inspections[i].get('inspection_date')) -
                    self.get_date(sorted_inspections[i-1].get('inspection_date'))
                ).days
                intervals.append(days)

            avg_interval = np.mean(intervals)
            std_interval = np.std(intervals) if len(intervals) > 1 else 30
        else:
            avg_interval = self.model_config['inspection_interval_days']
            std_interval = 30

        # Predict next date
        latest_date = self.get_date(sorted_inspections[-1].get('inspection_date'))
        predicted_date = latest_date + timedelta(days=int(avg_interval))

        # Predict score based on trend
        predicted_score, confidence = self._predict_score_trend(sorted_inspections)

        # Identify risk factors
        risk_factors = self._identify_risk_factors(sorted_inspections)

        # Generate recommendations
        recommendations = self._generate_pre_inspection_recommendations(
            sorted_inspections,
            predicted_date,
            risk_factors
        )

        return InspectionPrediction(
            predicted_date=predicted_date,
            predicted_score=predicted_score,
            confidence=confidence,
            risk_factors=risk_factors,
            recommendations=recommendations
        )

    def _predict_score_trend(self, inspections: List[Dict]) -> Tuple[int, float]:
        """Predict next inspection score based on trend"""
        scores = [i.get('score') for i in inspections if i.get('score') is not None]

        if not scores:
            return 75, 20.0

        if len(scores) == 1:
            return scores[0], 40.0

        # Calculate trend
        scores_array = np.array(scores)
        trend = np.polyfit(range(len(scores)), scores_array, 1)[0]

        # Predict next score
        last_score = scores[-1]
        predicted_score = last_score + trend

        # Round to integer and clamp
        predicted_score = int(min(100, max(0, predicted_score)))

        # Calculate confidence based on consistency
        score_std = np.std(scores_array)
        consistency = max(0, 100 - score_std)  # Higher = more consistent
        confidence = min(80, consistency + (len(scores) * 5))

        return predicted_score, confidence

    def _identify_risk_factors(self, inspections: List[Dict]) -> List[str]:
        """Identify risk factors from inspection history"""
        risk_factors = []

        # Check for recurring violations
        violation_counts = {}
        for inspection in inspections:
            for violation in inspection.get('violations', []):
                category = violation.get('category', 'other')
                violation_counts[category] = violation_counts.get(category, 0) + 1

        # Recurring violations
        recurring = [cat for cat, count in violation_counts.items() if count >= 2]
        if recurring:
            risk_factors.append(f"Recurring violations: {', '.join(recurring)}")

        # Check recent score trend
        if len(inspections) >= 2:
            latest_score = inspections[-1].get('score')
            previous_score = inspections[-2].get('score')

            if latest_score and previous_score:
                if latest_score < previous_score - 10:
                    risk_factors.append("Declining score trend")
                elif latest_score < 70:
                    risk_factors.append("Recent score below 70")

        # Check for critical violations
        recent = inspections[-1] if inspections else None
        if recent:
            for violation in recent.get('violations', []):
                if violation.get('severity') == 'critical':
                    risk_factors.append(f"Recent critical: {violation.get('description', '')}")

        return risk_factors if risk_factors else ['No significant risk factors identified']

    def _generate_pre_inspection_recommendations(
        self,
        inspections: List[Dict],
        predicted_date: datetime,
        risk_factors: List[str]
    ) -> List[str]:
        """Generate recommendations before next inspection"""
        recommendations = []
        days_until = (predicted_date - datetime.now()).days

        if days_until < 30:
            recommendations.append("URGENT: Inspection due within 30 days")
            recommendations.append("Schedule immediate self-inspection")
            recommendations.append("Address all critical violations")

        if days_until < 90:
            recommendations.append("Schedule mock inspection within 2 weeks")
            recommendations.append("Review all compliance documentation")

        # Based on risk factors
        for risk in risk_factors:
            if 'Recurring' in risk:
                recommendations.append("Implement additional monitoring for recurring violation areas")
            if 'Declining' in risk:
                recommendations.append("Staff refresher training on food safety protocols")

        # General recommendations
        recommendations.extend([
            "Update all food safety logs and documentation",
            "Verify all equipment is functioning properly",
            "Conduct full facility walkthrough with manager"
        ])

        return list(set(recommendations))  # Remove duplicates

    def predict_financial_impact(
        self,
        inspection_data: List[Dict],
        restaurant_seats: int = 50
    ) -> Dict:
        """Predict financial impact of compliance issues"""

        if not inspection_data:
            return {
                'estimated_annual_fines': 0,
                'estimated_insurance_increase': 0,
                'estimated_revenue_impact': 0,
                'total_annual_impact': 0,
            }

        latest = max(inspection_data, key=lambda x: self.get_date(x.get('inspection_date')))
        score = latest.get('score', 100)

        # Estimate fines based on score
        if score < 70:
            critical_count = sum(
                1 for v in latest.get('violations', [])
                if v.get('severity') == 'critical'
            )
            estimated_fines = 500 * (1 + critical_count * 2)
        else:
            estimated_fines = 0

        # Insurance premium increase (typically 10-30% for poor compliance)
        if score < 70:
            base_premium = 200 * (restaurant_seats / 50)  # Estimate
            insurance_increase = base_premium * 0.20
        else:
            insurance_increase = 0

        # Revenue impact from temporary closure
        if score < 60:
            daily_revenue = 100 * restaurant_seats / 50  # Rough estimate
            closure_days = (100 - score) / 10
            revenue_impact = daily_revenue * closure_days
        else:
            revenue_impact = 0

        total_impact = estimated_fines + insurance_increase + revenue_impact

        return {
            'estimated_annual_fines': int(estimated_fines),
            'estimated_insurance_increase': int(insurance_increase),
            'estimated_revenue_impact': int(revenue_impact),
            'total_annual_impact': int(total_impact),
        }

    def get_date(self, date_input) -> datetime:
        """Safely convert various date formats to datetime"""
        if isinstance(date_input, datetime):
            return date_input
        elif isinstance(date_input, str):
            try:
                return datetime.fromisoformat(date_input)
            except:
                return datetime.now()
        else:
            return datetime.now()


class CompetitorIntelligence:
    """Track competitor installations and market penetration"""

    def detect_competitor_installations(
        self,
        restaurant_name: str,
        address: str,
        public_records: List[Dict] = None
    ) -> Dict:
        """Detect if competitor has installed similar systems"""

        # Check inspection records for mentions of digital monitoring
        indicators = [
            'digital temperature monitoring',
            'automated temperature logs',
            'wireless sensors',
            'iot devices',
            'healthguard',
            'compuware',
            'jolt',
            'happy cow',
        ]

        has_monitoring = False
        competitor = None

        if public_records:
            for record in public_records:
                notes = record.get('notes', '') + ' ' + str(record.get('violations', []))

                for indicator in indicators:
                    if indicator.lower() in notes.lower():
                        has_monitoring = True
                        if indicator != 'digital temperature monitoring' and indicator != 'automated temperature logs':
                            competitor = indicator
                        break

        return {
            'has_monitoring': has_monitoring,
            'detected_competitor': competitor,
            'confidence': 'high' if competitor else 'medium' if has_monitoring else 'low',
        }

    def calculate_market_penetration(
        self,
        total_restaurants: int,
        competitor_installations: int
    ) -> Dict:
        """Calculate market penetration for an area"""

        penetration_rate = (competitor_installations / max(total_restaurants, 1)) * 100

        opportunity_score = 100 - penetration_rate

        return {
            'penetration_rate': penetration_rate,
            'opportunity_score': opportunity_score,
            'market_saturation': 'high' if penetration_rate > 50 else 'medium' if penetration_rate > 25 else 'low',
        }
