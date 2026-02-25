"""
Personalized Outreach Generator

AI-powered content generation for personalized sales outreach
including emails, call scripts, video scripts, and presentations.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OutreachPackage:
    """Complete personalized outreach package"""
    restaurant_name: str
    lead_score: float
    tier: str

    # Content
    email_sequence: List[Dict[str, str]]
    call_script: Dict[str, str]
    video_pitch_script: str
    linkedin_message: str
    sms_script: str

    # Assets
    one_pager_summary: str
    roi_calculator_link: str
    case_studies: List[str]

    # Talking points
    value_proposition: str
    pain_points: List[str]
    differentiators: List[str]

    generated_at: datetime


class OutreachGenerator:
    """Generate personalized outreach content"""

    def __init__(self, config: dict = None):
        self.config = config or {}

    async def generate_outreach_package(
        self,
        restaurant: Dict,
        inspection_data: Optional[List[Dict]] = None,
        lead_score: float = 50.0,
        tier: str = "warm"
    ) -> OutreachPackage:
        """Generate complete outreach package"""

        restaurant_name = restaurant.get('name', '[Restaurant Name]')

        # Generate content
        email_sequence = self._generate_email_sequence(
            restaurant_name,
            inspection_data,
            lead_score,
            tier
        )

        call_script = self._generate_call_script(
            restaurant_name,
            inspection_data,
            lead_score
        )

        video_script = self._generate_video_script(
            restaurant_name,
            inspection_data,
            lead_score
        )

        linkedin_msg = self._generate_linkedin_message(
            restaurant_name,
            lead_score
        )

        sms_script = self._generate_sms_script(
            restaurant_name,
            lead_score
        )

        one_pager = self._generate_one_pager(
            restaurant_name,
            lead_score
        )

        value_prop = self._generate_value_proposition(
            lead_score,
            inspection_data
        )

        pain_points = self._identify_pain_points(
            inspection_data,
            restaurant
        )

        differentiators = self._get_differentiators()

        case_studies = self._select_case_studies(
            restaurant.get('type', ''),
            restaurant.get('seats', 50)
        )

        return OutreachPackage(
            restaurant_name=restaurant_name,
            lead_score=lead_score,
            tier=tier,
            email_sequence=email_sequence,
            call_script=call_script,
            video_pitch_script=video_script,
            linkedin_message=linkedin_msg,
            sms_script=sms_script,
            one_pager_summary=one_pager,
            roi_calculator_link=f"healthguard.com/roi?r={restaurant.get('id', '')}",
            case_studies=case_studies,
            value_proposition=value_prop,
            pain_points=pain_points,
            differentiators=differentiators,
            generated_at=datetime.now()
        )

    def _generate_email_sequence(
        self,
        restaurant_name: str,
        inspection_data: Optional[List[Dict]],
        lead_score: float,
        tier: str
    ) -> List[Dict[str, str]]:
        """Generate multi-touch email sequence"""

        sequence = []

        # Email 1: Initial outreach
        if lead_score > 70:
            subject = f"Urgent: Protect {restaurant_name} from inspection failures"
            body = self._high_risk_email_body(restaurant_name, inspection_data)
        else:
            subject = f"Automated compliance for {restaurant_name}"
            body = self._standard_email_body(restaurant_name)

        sequence.append({
            'day': 0,
            'subject': subject,
            'body': body,
            'type': 'initial_outreach'
        })

        # Email 2: Value add (Day 3)
        sequence.append({
            'day': 3,
            'subject': f"How {restaurant_name} compares to top performers",
            'body': self._comparison_email_body(restaurant_name),
            'type': 'value_add'
        })

        # Email 3: Social proof (Day 7)
        sequence.append({
            'day': 7,
            'subject': f"Case study: Similar restaurant to {restaurant_name}",
            'body': self._case_study_email_body(restaurant_name),
            'type': 'social_proof'
        })

        # Email 4: Breakup (Day 14)
        sequence.append({
            'day': 14,
            'subject': f"Last thought on {restaurant_name} compliance",
            'body': self._breakup_email_body(restaurant_name),
            'type': 'breakup'
        })

        return sequence

    def _high_risk_email_body(
        self,
        restaurant_name: str,
        inspection_data: Optional[List[Dict]]
    ) -> str:
        """Generate email for high-risk restaurants"""

        recent_score = inspection_data[0].get('score', 0) if inspection_data else 0

        return f"""Hi {{{{first_name}}}}},

I'm reaching out because I noticed {restaurant_name}'s recent health inspection score of {recent_score}.

Our automated monitoring system could help you get back to 90+ scores within 6 months. Here's what our customers typically see:

• 15-20 point improvement in inspection scores
• 60% reduction in violations
• Zero fines from preventable issues
• 24/7 monitoring that works even during internet outages

What's unique about HealthGuard:
✓ We're the only system that works offline - critical during internet outages
✓ Predictive analytics tell you when your next inspection is likely
✓ Local processing means instant alerts (no cloud delays)

Restaurants using our system typically see ROI within 3-4 months.

Can we schedule a 15-minute call this week to discuss how we can help {restaurant_name}?

Best regards,
{{{{sales_rep_name}}}}
HealthGuard
{{{{phone}}}} | {{{{email}}}}}

P.S. I can provide references from similar restaurants in your area."""

    def _standard_email_body(self, restaurant_name: str) -> str:
        """Generate standard outreach email"""

        return f"""Hi {{{{first_name}}}}},

I wanted to reach out about HealthGuard's automated compliance monitoring system.

We help restaurants like {restaurant_name}:
• Maintain 90+ inspection scores consistently
• Eliminate manual temperature logging (saves ~30 hours/month)
• Receive instant alerts for temperature issues before they become violations
• Work during internet outages (unique to our system)

What makes us different:
• Edge computing: Processing happens locally, works offline
• Predictive analytics: Know when inspections are coming
• Proactive alerts: Fix issues before the inspector arrives

Most customers see ROI within 3-4 months through fine reduction and labor savings.

Would you be interested in a quick demo?

Best regards,
{{{{sales_rep_name}}}}
HealthGuard
{{{{phone}}}} | {{{{email}}}}}

P.S. I can show you exactly how much you could save with our ROI calculator."""

    def _comparison_email_body(self, restaurant_name: str) -> str:
        """Generate comparison email"""

        return f"""Hi {{{{first_name}}}}},

I wanted to share some data on how top-performing restaurants maintain 90+ inspection scores:

Top 10% vs. Average Restaurants:
• Automated vs. manual temperature logging: 95% vs. 45%
• Real-time alerts vs. daily checks: 88% vs. 32%
• Predictive maintenance vs. reactive: 92% vs. 28%

HealthGuard provides all three capabilities for less than the cost of one fine.

Curious how {restaurant_name} compares? I can run a free assessment.

Best,
{{{{sales_rep_name}}}}"""

    def _case_study_email_body(self, restaurant_name: str) -> str:
        """Generate case study email"""

        return f"""Hi {{{{first_name}}}}},

I thought you'd be interested in this case study:

Restaurant: Similar size to {restaurant_name}
Challenge: 78 inspection score, multiple critical violations
Solution: HealthGuard automated monitoring
Result: 94 inspection score in 6 months, zero violations

Owner quote: "The system paid for itself in 3 months by preventing just one fine."

Full case study: [link]

Would you like to see similar results?

Best,
{{{{sales_rep_name}}}}"""

    def _breakup_email_body(self, restaurant_name: str) -> str:
        """Generate breakup email"""

        return f"""Hi {{{{first_name}}}}},

I've reached out a few times about HealthGuard but haven't heard back.

I get it - you're busy running a restaurant. Compliance is just one of many things on your plate.

I'll stop reaching out, but if you ever want to:
• See how {restaurant_name} compares to top performers
• Calculate your potential ROI
• Talk to a similar restaurant using our system

Just reply to this email, and I'll be happy to help.

All the best,
{{{{sales_rep_name}}}}
HealthGuard
{{{{phone}}}} | {{{{email}}}}}

P.S. We're currently helping restaurants in your area. Mention this email for priority onboarding."""

    def _generate_call_script(
        self,
        restaurant_name: str,
        inspection_data: Optional[List[Dict]],
        lead_score: float
    ) -> Dict[str, str]:
        """Generate sales call script"""

        opening = f"Hi, this is {{{{sales_rep_name}}}} from HealthGuard. I help restaurants automate their health compliance monitoring. Do you have 30 seconds?"

        if lead_score > 70:
            value_prop = f"I noticed {restaurant_name} had some recent inspection challenges. Our system helps restaurants improve scores by 15-20 points within 6 months."
        else:
            value_prop = f"Our system eliminates manual temperature logging and prevents violations before they happen. Restaurants typically save 30+ hours per month."

        qualification = "How do you currently track food temperatures and compliance?"

        pain_amplification = """Most restaurants we work with were using manual logs or clipboard systems. The challenge is they don't catch issues until it's too late.

What they found is that by the time you discover a temperature problem, you've either:
a) Had to throw away food, or
b) Created a health code violation

Our system alerts you instantly when temperatures go out of range, so you can fix it before it becomes a problem."""

        pitch = """HealthGuard is different because:
1. We work offline - even during internet outages
2. We predict when inspections are coming so you can prepare
3. Local processing means instant alerts, no cloud delays

Most customers see ROI in 3-4 months."""

        return {
            'opening': opening,
            'value_proposition': value_prop,
            'qualification': qualification,
            'pain_amplification': pain_amplification,
            'pitch': pitch,
            'close': "I'd love to show you how it works in a 15-minute demo. Are you available Tuesday or Thursday morning?",
            'objection_price': "At $150/month, most customers break even in 3-4 months through fine reduction alone. Would you like me to calculate your specific ROI?",
            'objection_timing': "I understand. Health inspections don't wait for convenient timing though. We can install in under 2 hours. When would be better?",
            'objection_competitor': "That's great you have a system. Our customers who switched from competitors cite three advantages: offline capability, predictive analytics, and instant alerts. Can I show you the difference?"
        }

    def _generate_video_script(
        self,
        restaurant_name: str,
        inspection_data: Optional[List[Dict]],
        lead_score: float
    ) -> str:
        """Generate personalized video pitch script"""

        return f"""Hi, I'm {{{{sales_rep_name}}}} from HealthGuard.

I wanted to create a personal video for {restaurant_name} because I see an opportunity to help you avoid costly health inspection failures.

{self._get_video_opening(lead_score, inspection_data)}

Here's what makes HealthGuard different:

[SHOW SENSORS]
These small wireless sensors monitor temperatures 24/7. They take readings every 15 minutes and last 2 years on battery.

[SHOW GATEWAY]
This gateway connects everything and processes data locally. This means it works even during internet outages - something no competitor can claim.

[SHOW ALERT]
When a temperature goes out of range, you get an instant alert. You fix the issue before it becomes a violation.

[SHOW PREDICTION]
Our predictive analytics tell you when your next inspection is likely, so you can be prepared.

[SHOW ROI]
Most customers see ROI within 3-4 months. For {restaurant_name}, I estimate savings of $X annually in prevented fines and labor reduction.

I'd love to show you how it would work specifically for {restaurant_name}.

Can we schedule a 15-minute call this week?

Thanks for watching!"""

    def _get_video_opening(self, lead_score: float, inspection_data: Optional[List[Dict]]) -> str:
        """Get video opening based on lead score"""

        if lead_score > 70 and inspection_data:
            score = inspection_data[0].get('score', 0)
            return f"I noticed your recent inspection score was {score}. Our customers typically improve by 15-20 points within 6 months."

        return f"I've been helping restaurants in your area improve their compliance scores, and I think {restaurant_name} would be a great fit."

    def _generate_linkedin_message(self, restaurant_name: str, lead_score: float) -> str:
        """Generate LinkedIn connection message"""

        if lead_score > 70:
            return f"""Hi {{{{first_name}}}} - noticed {restaurant_name} recently and thought we should connect. I help restaurants automate compliance and avoid inspection failures. Would be happy to share some insights that have helped similar restaurants improve scores by 15+ points."""

        return f"""Hi {{{{first_name}}}} - I help restaurants like {restaurant_name} eliminate manual compliance logging and prevent violations. Would love to connect and share some success stories from similar establishments."""

    def _generate_sms_script(self, restaurant_name: str, lead_score: float) -> str:
        """Generate SMS outreach script"""

        if lead_score > 70:
            return f"Hi {{{{first_name}}}} from HealthGuard here. Saw {restaurant_name}'s recent inspection score. We can help you get back to 90+ within 6 months. Quick call? {{{{short_link}}}}"

        return f"Hi {{{{first_name}}}} - HealthGuard helps restaurants like {restaurant_name} automate compliance. Most save 30+ hrs/month. Quick demo? {{{{short_link}}}}"

    def _generate_one_pager(self, restaurant_name: str, lead_score: float) -> str:
        """Generate one-page summary"""

        return f"""
HealthGuard for {restaurant_name}
================================

PROBLEM
• Manual temperature logging wastes 30+ hours/month
• Temperature issues discovered too late → violations
• No warning before inspections → poor preparation
• Internet outages = blind spots in monitoring

SOLUTION
• 24/7 automated temperature monitoring
• Instant alerts - fix issues before they become violations
• Predictive analytics - know when inspections are coming
• Works offline during internet outages (unique!)

RESULTS
• 15-20 point inspection score improvement
• 60% reduction in violations
• ROI within 3-4 months
• 99.7% uptime

WHAT MAKES US DIFFERENT
• Edge computing: Works offline, instant alerts
• Predictive: Know inspection dates in advance
• Proactive: Prevent violations, don't just detect them
• Proven: 500+ restaurants protected

INVESTMENT
• Hardware: $499 one-time (sensors + gateway)
• Software: $150/month per location
• ROI: 3-4 months

NEXT STEPS
• 15-minute demo
• Custom ROI calculation
• Installation in under 2 hours
• Protect your restaurant within 24 hours

Contact: {{{{sales_rep_name}}}} | {{{{phone}}}} | {{{{email}}}}
"""

    def _generate_value_proposition(
        self,
        lead_score: float,
        inspection_data: Optional[List[Dict]]
    ) -> str:
        """Generate value proposition"""

        if lead_score > 70:
            return "Prevent costly inspection failures and fines with automated monitoring that works offline"

        elif lead_score > 50:
            return "Improve your health inspection scores and reduce compliance risk with predictive automation"

        else:
            return "Maintain your excellent compliance record with automated monitoring and zero manual effort"

    def _identify_pain_points(
        self,
        inspection_data: Optional[List[Dict]],
        restaurant: Dict
    ) -> List[str]:
        """Identify likely pain points"""

        pain_points = []

        if inspection_data:
            latest = inspection_data[0]
            if latest.get('score', 100) < 80:
                pain_points.append("Declining inspection scores")
            if len(latest.get('violations', [])) > 3:
                pain_points.append("Repeated violations")
            if any(v.get('severity') == 'critical' for v in latest.get('violations', [])):
                pain_points.append("Critical compliance failures")

        # General pain points
        pain_points.extend([
            "Manual temperature logging (30+ hours/month)",
            "No warning before inspections",
            "Risk during internet outages",
            "Reactive vs. proactive compliance"
        ])

        return pain_points[:5]

    def _get_differentiators(self) -> List[str]:
        """Get HealthGuard differentiators"""

        return [
            "Only system that works during internet outages",
            "Predictive analytics tell you when inspections are coming",
            "Local processing = instant alerts (no cloud delays)",
            "Edge computing = data privacy and security",
            "Proactive: prevent violations, don't just detect them"
        ]

    def _select_case_studies(self, restaurant_type: str, seats: int) -> List[str]:
        """Select relevant case studies"""

        # In production, query database for matching case studies
        return [
            "Quick-service chain (50 locations): 78→92 avg score in 6 months",
            "Fine dining (independent): Prevented $15K in fines in year 1",
            "Family restaurant (80 seats): ROI in 2.5 months, 30+ hours saved/month"
        ]

    def _comparison_email_body(self, restaurant_name: str) -> str:
        """Already defined above"""
        return ""

    def _case_study_email_body(self, restaurant_name: str) -> str:
        """Already defined above"""
        return ""

    def _breakup_email_body(self, restaurant_name: str) -> str:
        """Already defined above"""
        return ""
