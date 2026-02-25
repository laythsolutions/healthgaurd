"""
Social Review Monitoring System

Monitors social media platforms (Yelp, Google Reviews, TripAdvisor, etc.)
for mentions of food safety, health issues, and compliance-related topics
that can indicate potential problems before inspections occur.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class Sentiment(Enum):
    """Sentiment classification"""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


@dataclass
class SocialMention:
    """A social media post/review mentioning the restaurant"""
    platform: str  # 'yelp', 'google', 'tripadvisor', etc.
    review_id: str
    restaurant_name: str
    restaurant_address: str
    author: str
    rating: int  # 1-5 stars
    text: str
    post_date: datetime

    # Analysis
    sentiment: Sentiment
    compliance_mentions: List[str]  # 'food poisoning', 'dirty', etc.
    severity: str  # 'low', 'medium', 'high', 'critical'
    verified: bool  # Verified purchase/visit

    # Metrics
    likes: int
    comments: int
    shares: int

    raw_data: dict


class SocialReviewMonitor:
    """Monitors social reviews for compliance-related mentions"""

    def __init__(self, config: dict):
        self.config = config
        self.compliance_keywords = self._load_compliance_keywords()
        self.sentiment_analyzer = SentimentAnalyzer()

    def _load_compliance_keywords(self) -> Dict[str, List[str]]:
        """Load compliance-related keywords by category"""

        return {
            'food_illness': [
                'food poisoning', 'sick', 'vomiting', 'nausea', 'diarrhea',
                'stomach ache', 'food borne illness', 'undercooked',
                'raw meat', 'cold food', 'expired'
            ],
            'cleanliness': [
                'dirty', 'filthy', 'unsanitary', 'gross', 'roaches', 'bugs',
                'rodents', 'mice', 'rats', 'cockroach', 'pest', 'insects',
                'hair in food', 'dirty bathroom', 'sticky tables', 'greasy'
            ],
            'temperature': [
                'cold food', 'lukewarm', 'not hot enough', 'cold entree',
                'frozen food', 'ice cold', 'should be hot', 'warm salad'
            ],
            'staff_hygiene': [
                'dirty hands', 'no gloves', 'coughing', 'sneezing',
                'nose picking', 'dirty uniform', 'unprofessional',
                'touching face', 'not washing hands'
            ],
            'pests': [
                'roach', 'rodent', 'mouse', 'rat', 'bug', 'insect',
                'flies', 'ants', 'gnats', 'pest control', 'exterminator'
            ],
            'violations': [
                'health inspector', 'health department', 'shut down',
                'closed', 'violation', 'cited', 'failed inspection',
                'health code', 'grade card'
            ]
        }

    async def monitor_restaurant_reviews(
        self,
        restaurant_name: str,
        address: str,
        days_back: int = 30
    ) -> List[SocialMention]:
        """
        Monitor reviews for a specific restaurant

        Queries multiple platforms and filters for compliance mentions
        """

        mentions = []

        # Query each platform
        yelp_mentions = await self._query_yelp(restaurant_name, address, days_back)
        google_mentions = await self._query_google_reviews(restaurant_name, address, days_back)
        tripadvisor_mentions = await self._query_tripadvisor(restaurant_name, address, days_back)

        mentions.extend(yelp_mentions)
        mentions.extend(google_mentions)
        mentions.extend(tripadvisor_mentions)

        # Analyze for compliance mentions
        analyzed_mentions = []
        for mention in mentions:
            analyzed = self._analyze_mention(mention)
            if analyzed.compliance_mentions:  # Only keep if compliance-related
                analyzed_mentions.append(analyzed)

        logger.info(f"Found {len(analyzed_mentions)} compliance-related mentions for {restaurant_name}")
        return analyzed_mentions

    async def _query_yelp(
        self,
        restaurant_name: str,
        address: str,
        days_back: int
    ) -> List[SocialMention]:
        """Query Yelp Fusion API for reviews"""

        # In production, use Yelp Fusion API
        # https://www.yelp.com/developers/documentation/v3/get_reviews

        # Mock response for demonstration
        return [
            SocialMention(
                platform='yelp',
                review_id='abc123',
                restaurant_name=restaurant_name,
                restaurant_address=address,
                author='YelpUser123',
                rating=1,
                text='I got food poisoning after eating here. The restaurant was dirty and I saw a roach. Health inspector needs to visit.',
                post_date=datetime.now() - timedelta(days=5),
                sentiment=Sentiment.VERY_NEGATIVE,
                compliance_mentions=['food_illness', 'cleanliness', 'pests', 'violations'],
                severity='critical',
                verified=True,
                likes=5,
                comments=2,
                shares=0,
                raw_data={}
            )
        ]

    async def _query_google_reviews(
        self,
        restaurant_name: str,
        address: str,
        days_back: int
    ) -> List[SocialMention]:
        """Query Google Places API for reviews"""

        # In production, use Google Places API
        # https://developers.google.com/places/web-service/details

        return []

    async def _query_tripadvisor(
        self,
        restaurant_name: str,
        address: str,
        days_back: int
    ) -> List[SocialMention]:
        """Query TripAdvisor API for reviews"""

        # TripAdvisor doesn't have a public API
        # Would need web scraping in production

        return []

    def _analyze_mention(self, mention: SocialMention) -> SocialMention:
        """Analyze a review for compliance-related content"""

        text_lower = mention.text.lower()

        # Check for compliance keywords
        compliance_categories = []
        for category, keywords in self.compliance_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    compliance_categories.append(category)
                    break

        mention.compliance_mentions = compliance_categories

        # Calculate severity
        mention.severity = self._calculate_severity(
            compliance_categories,
            mention.rating,
            mention.sentiment
        )

        return mention

    def _calculate_severity(
        self,
        categories: List[str],
        rating: int,
        sentiment: Sentiment
    ) -> str:
        """Calculate severity level of the mention"""

        score = 0

        # High-risk categories
        if 'food_illness' in categories:
            score += 40
        if 'pests' in categories:
            score += 30
        if 'violations' in categories:
            score += 30

        # Multiple categories increase severity
        if len(categories) >= 3:
            score += 20
        elif len(categories) >= 2:
            score += 10

        # Low rating increases severity
        if rating == 1:
            score += 20
        elif rating == 2:
            score += 10

        # Negative sentiment increases severity
        if sentiment == Sentiment.VERY_NEGATIVE:
            score += 15
        elif sentiment == Sentiment.NEGATIVE:
            score += 5

        # Determine severity level
        if score >= 70:
            return 'critical'
        elif score >= 50:
            return 'high'
        elif score >= 30:
            return 'medium'
        else:
            return 'low'

    async def generate_compliance_alert(
        self,
        mentions: List[SocialMention]
    ) -> Optional[dict]:
        """
        Generate an alert if compliance mentions exceed threshold

        Triggers alert when:
        - 3+ critical mentions in 7 days
        - 5+ high mentions in 7 days
        - Any verified food illness mention
        """

        if not mentions:
            return None

        critical_count = len([m for m in mentions if m.severity == 'critical'])
        high_count = len([m for m in mentions if m.severity == 'high'])
        food_illness_mentions = [
            m for m in mentions
            if 'food_illness' in m.compliance_mentions and m.verified
        ]

        should_alert = (
            critical_count >= 3 or
            high_count >= 5 or
            len(food_illness_mentions) >= 1
        )

        if should_alert:
            alert = {
                'alert_type': 'social_media_compliance_risk',
                'severity': self._calculate_overall_severity(mentions),
                'restaurant_name': mentions[0].restaurant_name,
                'mention_counts': {
                    'critical': critical_count,
                    'high': high_count,
                    'medium': len([m for m in mentions if m.severity == 'medium']),
                    'low': len([m for m in mentions if m.severity == 'low'])
                },
                'categories_mentioned': self._aggregate_categories(mentions),
                'sample_mentions': [
                    {
                        'platform': m.platform,
                        'text': m.text,
                        'rating': m.rating,
                        'date': m.post_date.strftime('%Y-%m-%d')
                    }
                    for m in sorted(mentions, key=lambda x: x.severity, reverse=True)[:5]
                ],
                'recommendation': self._generate_recommendation(mentions),
                'created_at': datetime.now().isoformat()
            }

            return alert

        return None

    def _calculate_overall_severity(self, mentions: List[SocialMention]) -> str:
        """Calculate overall severity from multiple mentions"""

        critical_count = len([m for m in mentions if m.severity == 'critical'])

        if critical_count >= 3:
            return 'critical'
        elif critical_count >= 1:
            return 'high'
        else:
            return 'medium'

    def _aggregate_categories(self, mentions: List[SocialMention]) -> Dict[str, int]:
        """Aggregate mention counts by category"""

        category_counts = {}
        for mention in mentions:
            for category in mention.compliance_mentions:
                category_counts[category] = category_counts.get(category, 0) + 1

        return category_counts

    def _generate_recommendation(self, mentions: List[SocialMention]) -> str:
        """Generate actionable recommendation based on mentions"""

        categories = self._aggregate_categories(mentions)

        if 'food_illness' in categories:
            return (
                "URGENT: Multiple customers reported food poisoning symptoms. "
                "Immediate internal investigation required. Review food handling "
                "procedures, temperature logs, and staff hygiene. Consider "
                "proactive health department consultation."
            )
        elif 'pests' in categories:
            return (
                "Pest sightings reported by customers. Schedule immediate "
                "pest control inspection and treatment. Check food storage "
                "and sealing of entry points."
            )
        elif 'cleanliness' in categories:
            return (
                "Cleanliness concerns raised by customers. Conduct deep cleaning "
                "of dining area and bathrooms. Review cleaning schedules and "
                "staff compliance."
            )
        else:
            return (
                "Compliance concerns mentioned in reviews. Review all "
                "operational procedures and conduct staff retraining."
            )

    async def batch_monitor_restaurants(
        self,
        restaurants: List[dict],
        days_back: int = 30
    ) -> Dict[str, dict]:
        """Monitor multiple restaurants in batch"""

        alerts = {}
        for restaurant in restaurants:
            mentions = await self.monitor_restaurant_reviews(
                restaurant_name=restaurant['name'],
                address=restaurant['address'],
                days_back=days_back
            )

            alert = await self.generate_compliance_alert(mentions)
            if alert:
                key = f"{restaurant['state']}:{restaurant['city']}:{restaurant['name']}"
                alerts[key] = alert

        logger.info(f"Generated {len(alerts)} compliance alerts from social monitoring")
        return alerts


class SentimentAnalyzer:
    """Simple sentiment analyzer for review text"""

    def __init__(self):
        # Load positive/negative word lists
        self.positive_words = [
            'good', 'great', 'excellent', 'amazing', 'delicious', 'friendly',
            'clean', 'attentive', 'recommend', 'love', 'best', 'wonderful'
        ]

        self.negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'dirty', 'rude',
            'slow', 'cold', 'disgusting', 'worst', 'hate', 'never again'
        ]

    def analyze_sentiment(self, text: str) -> Sentiment:
        """Analyze sentiment of review text"""

        text_lower = text.lower()
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)

        score = positive_count - negative_count

        if score <= -3:
            return Sentiment.VERY_NEGATIVE
        elif score < 0:
            return Sentiment.NEGATIVE
        elif score == 0:
            return Sentiment.NEUTRAL
        elif score < 3:
            return Sentiment.POSITIVE
        else:
            return Sentiment.VERY_POSITIVE
