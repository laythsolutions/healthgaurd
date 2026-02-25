"""
Dynamic ROI Calculator

Real-time ROI calculations using actual restaurant data including
fine history, operational costs, and industry benchmarks.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ROICalculation:
    """Comprehensive ROI calculation result"""
    restaurant_name: str

    # Investment
    hardware_cost: float
    monthly_software_cost: float
    annual_software_cost: float
    total_first_year_cost: float

    # Savings (annual)
    fine_reduction_savings: float
    labor_savings: float
    food_waste_reduction: float
    insurance_premium_reduction: float
    total_annual_savings: float

    # ROI metrics
    payback_period_months: float
    three_year_roi: float
    five_year_roi: float
    annual_roi_percentage: float

    # Breakdown
    monthly_break_even: float
    savings_breakdown: Dict[str, float]

    calculated_at: datetime


class DynamicROICalculator:
    """Calculate ROI using real restaurant data and benchmarks"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.benchmarks = self._load_benchmarks()

    def _load_benchmarks(self) -> Dict:
        """Load industry benchmarks for ROI calculations"""

        return {
            # Fine benchmarks (per violation)
            'critical_violation_fine': 750,
            'major_violation_fine': 350,
            'minor_violation_fine': 100,

            # Labor savings
            'manual_logging_hours_per_week': 8,
            'average_hourly_labor_cost': 15,

            # Food waste (per incident)
            'temperature_incident_waste_cost': 150,

            # Insurance
            'insurance_premium_reduction_percent': 15,
            'average_annual_premium': 3500,

            # Inspection score improvement
            'average_score_improvement': 15,

            # Violation reduction
            'average_violation_reduction': 0.60
        }

    async def calculate_roi(
        self,
        restaurant: Dict,
        inspection_data: Optional[List[Dict]] = None,
        current_fines: Optional[float] = None
    ) -> ROICalculation:
        """Calculate comprehensive ROI"""

        restaurant_name = restaurant.get('name', 'Restaurant')

        # Get restaurant parameters
        seats = restaurant.get('seats', 50)
        sensors_needed = max(5, seats // 20)  # 1 sensor per 20 seats

        # Calculate investment costs
        hardware_cost = 499 + (sensors_needed * 50)  # Base kit + additional sensors
        monthly_software_cost = self._calculate_tiered_pricing(seats)
        annual_software_cost = monthly_software_cost * 12
        total_first_year = hardware_cost + annual_software_cost

        # Calculate savings
        fine_savings = await self._calculate_fine_savings(
            inspection_data,
            current_fines
        )

        labor_savings = self._calculate_labor_savings(seats)
        waste_savings = self._calculate_food_waste_savings(
            inspection_data,
            seats
        )
        insurance_savings = self._calculate_insurance_savings(seats)

        total_annual_savings = (
            fine_savings +
            labor_savings +
            waste_savings +
            insurance_savings
        )

        # Calculate ROI metrics
        payback_months = (total_first_year / total_annual_savings) * 12
        three_year_value = (total_annual_savings * 3) - total_first_year - (annual_software_cost * 2)
        five_year_value = (total_annual_savings * 5) - total_first_year - (annual_software_cost * 4)
        annual_roi = (total_annual_savings / total_first_year) * 100

        return ROICalculation(
            restaurant_name=restaurant_name,
            hardware_cost=hardware_cost,
            monthly_software_cost=monthly_software_cost,
            annual_software_cost=annual_software_cost,
            total_first_year_cost=total_first_year,
            fine_reduction_savings=fine_savings,
            labor_savings=labor_savings,
            food_waste_reduction=waste_savings,
            insurance_premium_reduction=insurance_savings,
            total_annual_savings=total_annual_savings,
            payback_period_months=round(payback_months, 1),
            three_year_roi=round(three_year_value, 0),
            five_year_roi=round(five_year_value, 0),
            annual_roi_percentage=round(annual_roi, 1),
            monthly_break_even=round(total_annual_savings / 12, 0),
            savings_breakdown={
                'Fine Reduction': fine_savings,
                'Labor Savings': labor_savings,
                'Food Waste Reduction': waste_savings,
                'Insurance Premium Reduction': insurance_savings
            },
            calculated_at=datetime.now()
        )

    def _calculate_tiered_pricing(self, seats: int) -> float:
        """Calculate monthly subscription based on restaurant size"""

        if seats <= 50:
            return 129  # Starter
        elif seats <= 100:
            return 169  # Standard
        elif seats <= 200:
            return 249  # Professional
        else:
            return 349  # Enterprise

    async def _calculate_fine_savings(
        self,
        inspection_data: Optional[List[Dict]],
        current_fines: Optional[float]
    ) -> float:
        """Calculate annual fine reduction savings"""

        if current_fines:
            # Use actual fine history
            # Assume 60% reduction with HealthGuard
            return current_fines * self.benchmarks['average_violation_reduction']

        if not inspection_data:
            # Use benchmark
            return self.benchmarks['critical_violation_fine'] * 4  # Assume 4 per year

        # Calculate from inspection data
        latest = inspection_data[0]
        violations = latest.get('violations', [])

        fine_potential = 0
        for violation in violations:
            severity = violation.get('severity', 'minor')
            if severity == 'critical':
                fine_potential += self.benchmarks['critical_violation_fine']
            elif severity == 'major':
                fine_potential += self.benchmarks['major_violation_fine']
            else:
                fine_potential += self.benchmarks['minor_violation_fine']

        # Assume same violations repeat without intervention
        # 60% reduction with HealthGuard
        return fine_potential * self.benchmarks['average_violation_reduction']

    def _calculate_labor_savings(self, seats: int) -> float:
        """Calculate annual labor savings from automated logging"""

        # Manual logging hours per week (scales with restaurant size)
        hours_per_week = self.benchmarks['manual_logging_hours_per_week']
        if seats > 100:
            hours_per_week += 4
        if seats > 200:
            hours_per_week += 6

        annual_hours = hours_per_week * 52
        labor_cost = annual_hours * self.benchmarks['average_hourly_labor_cost']

        # 100% of manual logging eliminated
        return labor_cost

    def _calculate_food_waste_savings(
        self,
        inspection_data: Optional[List[Dict]],
        seats: int
    ) -> float:
        """Calculate annual food waste reduction savings"""

        # Estimate temperature incidents per year
        # Larger restaurants = more incidents
        base_incidents_per_year = 4
        if seats > 100:
            base_incidents_per_year = 6
        if seats > 200:
            base_incidents_per_year = 8

        # Adjust based on inspection history
        if inspection_data:
            latest = inspection_data[0]
            temp_violations = [
                v for v in latest.get('violations', [])
                if 'temperature' in v.get('description', '').lower()
            ]
            if temp_violations:
                base_incidents_per_year += len(temp_violations) * 2  # Likely recurring

        # 80% reduction with proactive alerts
        incidents_prevented = base_incidents_per_year * 0.8
        savings = incidents_prevented * self.benchmarks['temperature_incident_waste_cost']

        return savings

    def _calculate_insurance_savings(self, seats: int) -> float:
        """Calculate annual insurance premium reduction"""

        # Premium scales with restaurant size
        base_premium = self.benchmarks['average_annual_premium']
        if seats > 100:
            base_premium *= 1.3
        if seats > 200:
            base_premium *= 1.5

        # 15% reduction with verified compliance
        return base_premium * self.benchmarks['insurance_premium_reduction_percent'] / 100

    def generate_roi_summary(self, roi: ROICalculation) -> str:
        """Generate human-readable ROI summary"""

        return f"""
ROI Analysis for {roi.restaurant_name}
{'=' * 50}

INVESTMENT
• Hardware (one-time): ${roi.hardware_cost:,.0f}
• Monthly Software: ${roi.monthly_software_cost:,.0f}
• First Year Total: ${roi.total_first_year_cost:,.0f}

ANNUAL SAVINGS
• Fine Reduction: ${roi.fine_reduction_savings:,.0f}
• Labor Savings: ${roi.labor_savings:,.0f}
• Food Waste Prevention: ${roi.food_waste_reduction:,.0f}
• Insurance Reduction: ${roi.insurance_premium_reduction:,.0f}
• Total Annual Savings: ${roi.total_annual_savings:,.0f}

ROI METRICS
• Payback Period: {roi.payback_period_months:.1f} months
• 3-Year ROI: ${roi.three_year_roi:,.0f}
• 5-Year ROI: ${roi.five_year_roi:,.0f}
• Annual Return: {roi.annual_roi_percentage}%

MONTHLY BREAK-EVEN
• Need to save: ${roi.monthly_break_even:,.0f}/month
• You'll save: ${roi.total_annual_savings / 12:,.0f}/month
• Net monthly profit: ${roi.total_annual_savings / 12 - roi.monthly_software_cost:,.0f}

Bottom Line: HealthGuard pays for itself in {roi.payback_period_months:.0f} months
and generates ${roi.three_year_roi:,.0f} profit over 3 years.
"""


class ROIComparator:
    """Compare ROI across different scenarios"""

    def compare_scenarios(
        self,
        restaurant: Dict,
        scenarios: List[str] = None
    ) -> Dict[str, ROICalculation]:
        """Compare ROI across different scenarios"""

        calculator = DynamicROICalculator()
        scenarios = scenarios or ['current', 'with_healthguard']

        results = {}

        if 'current' in scenarios:
            # Current state (no HealthGuard)
            current_cost = self._calculate_current_annual_cost(restaurant)
            results['current'] = ROICalculation(
                restaurant_name=restaurant.get('name'),
                hardware_cost=0,
                monthly_software_cost=0,
                annual_software_cost=0,
                total_first_year_cost=current_cost,
                fine_reduction_savings=0,
                labor_savings=0,
                food_waste_reduction=0,
                insurance_premium_reduction=0,
                total_annual_savings=0,
                payback_period_months=0,
                three_year_roi=-current_cost * 3,
                five_year_roi=-current_cost * 5,
                annual_roi_percentage=0,
                monthly_break_even=0,
                savings_breakdown={},
                calculated_at=datetime.now()
            )

        if 'with_healthguard' in scenarios:
            results['with_healthguard'] = await calculator.calculate_roi(restaurant)

        return results

    def _calculate_current_annual_cost(self, restaurant: Dict) -> float:
        """Calculate current annual compliance cost"""

        seats = restaurant.get('seats', 50)
        hours_per_week = 8
        if seats > 100:
            hours_per_week += 4

        # Labor cost
        annual_hours = hours_per_week * 52
        labor_cost = annual_hours * 15  # $15/hour

        # Estimate fines (average)
        estimated_fines = 1500  # Industry average

        return labor_cost + estimated_fines
