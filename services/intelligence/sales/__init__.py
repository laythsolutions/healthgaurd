"""
Sales Enablement Platform - Complete Package

This module integrates all sales enablement components:
- Advanced Lead Scoring (6-factor model)
- Personalized Outreach Generation
- Dynamic ROI Calculator
- Competitive Battle Cards
- Territory Intelligence
- CRM Integration
"""

from .lead_scoring import (
    AdvancedLeadScoringEngine,
    LeadBatchProcessor,
    LeadScore,
    LeadTier
)
from .outreach_generator import (
    OutreachGenerator,
    OutreachPackage
)
from .roi_calculator import (
    DynamicROICalculator,
    ROICalculation,
    ROIComparator
)

__all__ = [
    'AdvancedLeadScoringEngine',
    'LeadBatchProcessor',
    'LeadScore',
    'LeadTier',
    'OutreachGenerator',
    'OutreachPackage',
    'DynamicROICalculator',
    'ROICalculation',
    'ROIComparator',
    'SalesEnablementPlatform'
]


class SalesEnablementPlatform:
    """
    Complete sales enablement platform

    Integrates all sales tools into a unified platform
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.lead_scorer = AdvancedLeadScoringEngine(config)
        self.outreach_generator = OutreachGenerator(config)
        self.roi_calculator = DynamicROICalculator(config)
        self.batch_processor = LeadBatchProcessor()

    async def generate_complete_sales_package(
        self,
        restaurant: Dict,
        inspection_data: Optional[List[Dict]] = None,
        market_intelligence: Optional[Dict] = None,
        competitor_data: Optional[Dict] = None
    ) -> Dict:
        """Generate complete sales package for a restaurant"""

        # Score the lead
        lead_score = await self.lead_scorer.score_lead(
            restaurant,
            inspection_data,
            market_intelligence,
            competitor_data
        )

        # Generate outreach package
        outreach = await self.outreach_generator.generate_outreach_package(
            restaurant,
            inspection_data,
            lead_score.overall_score,
            lead_score.tier.value
        )

        # Calculate ROI
        roi = await self.roi_calculator.calculate_roi(
            restaurant,
            inspection_data
        )

        # Generate battle card
        battle_card = self._generate_battle_card(
            restaurant,
            lead_score,
            roi,
            competitor_data
        )

        return {
            'restaurant': restaurant,
            'lead_score': {
                'overall_score': lead_score.overall_score,
                'tier': lead_score.tier.value,
                'health_risk': lead_score.health_risk_score,
                'acquisition_probability': lead_score.acquisition_probability,
                'urgency': lead_score.urgency
            },
            'outreach': {
                'email_sequence': outreach.email_sequence,
                'call_script': outreach.call_script,
                'video_script': outreach.video_pitch_script,
                'one_pager': outreach.one_pager_summary
            },
            'roi': {
                'payback_months': roi.payback_period_months,
                'three_year_value': roi.three_year_roi,
                'annual_savings': roi.total_annual_savings,
                'summary': self.roi_calculator.generate_roi_summary(roi)
            },
            'battle_card': battle_card,
            'next_steps': self._generate_next_steps(lead_score, roi)
        }

    def _generate_battle_card(
        self,
        restaurant: Dict,
        lead_score: LeadScore,
        roi: ROICalculation,
        competitor_data: Optional[Dict]
    ) -> Dict:
        """Generate competitive battle card"""

        return {
            'restaurant_name': restaurant.get('name'),
            'healthguard_advantages': [
                "Works offline during internet outages",
                "Predictive analytics for inspection dates",
                "Local processing = instant alerts",
                "Proactive: prevents, doesn't just detect"
            ],
            'competitor_weaknesses': [
                "Requires internet (cloud-dependent)",
                "No predictive capabilities",
                "Cloud delays on alerts",
                "Reactive: only detects after issue occurs"
            ],
            'roi_comparison': f"${roi.payback_period_months:.0f} month payback vs. competitor 12-18 months",
            'key_differentiators': lead_score.talking_points,
            'objection_handlers': lead_score.objection_handlers
        }

    def _generate_next_steps(
        self,
        lead_score: LeadScore,
        roi: ROICalculation
    ) -> List[str]:
        """Generate next steps based on lead quality"""

        steps = []

        if lead_score.tier == LeadTier.HOT:
            steps = [
                "Call within 4 hours",
                "Send high-urgency email immediately",
                "Schedule demo within 48 hours",
                "Prepare ROI report for review"
            ]
        elif lead_score.tier == LeadTier.WARM:
            steps = [
                "Send personalized email sequence",
                "Connect on LinkedIn",
                "Call within 48 hours",
                "Nurture with value-added content"
            ]
        elif lead_score.tier == LeadTier.COLD:
            steps = [
                "Add to nurture campaign",
                "Send monthly newsletter",
                "Monitor for trigger events",
                "Re-score in 90 days"
            ]
        else:
            steps = [
                "Do not pursue",
                "Add to do-not-contact list"
            ]

        return steps
