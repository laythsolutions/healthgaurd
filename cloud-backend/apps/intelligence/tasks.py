"""Celery tasks for data intelligence processing"""

from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import PublicInspectionData, LeadScore
from apps.restaurants.models import Restaurant

logger = logging.getLogger(__name__)


@shared_task
def harvest_public_inspection_data(state: str, days_back: int = 7):
    """Harvest public inspection data for a state"""
    logger.info(f"Harvesting {state} inspection data for last {days_back} days")

    try:
        # Import harvester (to avoid circular imports)
        import sys
        sys.path.append('/app/data-intelligence')
        from harvesters.state_harvesters import get_harvester

        # Configure harvester
        config = {
            'state': state,
            'base_url': get_state_api_url(state),
        }

        harvester = get_harvester(state, config)

        # Harvest data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days_back)

        records = harvester.harvest(start_date, end_date)

        # Store in database
        stored_count = 0
        for record in records:
            obj, created = PublicInspectionData.objects.get_or_create(
                restaurant_name=record.restaurant_name,
                address=record.address,
                city=record.city,
                state=record.state,
                inspection_date=record.inspection_date,
                defaults={
                    'dba_name': record.restaurant_name,
                    'zip_code': record.zip_code,
                    'inspection_score': record.score,
                    'violations_count': len(record.violations),
                    'critical_violations_count': sum(
                        1 for v in record.violations if v.get('severity') == 'critical'
                    ),
                    'violations_data': record.violations,
                    'risk_level': record.risk_level,
                    'data_source': 'STATE_API',
                }
            )
            if created:
                stored_count += 1

        logger.info(f"Harvested and stored {stored_count} new records for {state}")
        return stored_count

    except Exception as e:
        logger.error(f"Error harvesting {state} data: {e}")
        raise


@shared_task
def match_restaurants():
    """Match public inspection data with internal restaurants"""
    logger.info("Matching public inspection data with restaurants")

    matched_count = 0

    # Get unmatched public records
    unmatched = PublicInspectionData.objects.filter(matched=False)

    for public_record in unmatched:
        try:
            # Search for matching restaurant
            restaurant = Restaurant.objects.filter(
                name__icontains=public_record.restaurant_name,
                city__iexact=public_record.city,
                state=public_record.state
            ).first()

            if restaurant:
                public_record.matched_restaurant = restaurant
                public_record.matched = True
                public_record.save()
                matched_count += 1

        except Exception as e:
            logger.error(f"Error matching restaurant {public_record.restaurant_name}: {e}")

    logger.info(f"Matched {matched_count} restaurants")
    return matched_count


@shared_task
def calculate_lead_scores():
    """Calculate lead scores for all unmatched restaurants"""
    logger.info("Calculating lead scores")

    # Import scoring engine
    import sys
    sys.path.append('/app/data-intelligence')
    from processors.risk_scorer import LeadScoringEngine

    engine = LeadScoringEngine()

    scored_count = 0

    # Get public inspection data without lead scores
    public_records = PublicInspectionData.objects.filter(
        matched=False,
        processed=False
    )[:1000]  # Process in batches

    for public_record in public_records:
        try:
            # Gather inspection history
            inspections = PublicInspectionData.objects.filter(
                restaurant_name=public_record.restaurant_name,
                city=public_record.city,
                state=public_record.state
            ).values()

            # Build restaurant data
            restaurant_data = {
                'name': public_record.restaurant_name,
                'address': public_record.address,
                'city': public_record.city,
                'state': public_record.state,
                'seating_capacity': 100,  # Default if unknown
            }

            # Calculate lead score
            score = engine.calculate_lead_score(restaurant_data, list(inspections))

            # Create lead score record
            LeadScore.objects.create(
                restaurant_name=public_record.restaurant_name,
                address=public_record.address,
                city=public_record.city,
                state=public_record.state,
                lead_score=int(score['lead_score']),
                healthguard_risk_score=int(score['healthguard_risk']),
                acquisition_probability=int(score['acquisition_probability'] * 100),
                size_score=int(score.get('size_score', 50)),
                cuisine_risk_score=int(score.get('cuisine_risk', 50)),
                location_density_score=int(score.get('location_score', 50)),
                competitor_gap_score=int(score.get('competitor_gap', 50)),
                tech_readiness_score=int(score.get('tech_score', 50)),
                optimal_contact_date=timezone.now().date() + timedelta(days=score['optimal_timing']['optimal_days']),
                urgency_level=score['optimal_timing']['urgency'],
                recommended_approach=score['recommended_approach'],
                value_proposition=score['talking_points'][0] if score['talking_points'] else '',
                talking_points=score['talking_points'],
            )

            # Mark as processed
            public_record.processed = True
            public_record.save()

            scored_count += 1

        except Exception as e:
            logger.error(f"Error scoring {public_record.restaurant_name}: {e}")

    logger.info(f"Calculated {scored_count} lead scores")
    return scored_count


@shared_task
def generate_territory_intelligence(state: str, city: str = None):
    """Generate market intelligence for a territory"""
    logger.info(f"Generating intelligence for {state}, {city or 'all cities'}")

    # Implementation would aggregate stats for the territory
    # and create/update MarketIntelligence records

    return {"status": "completed"}


def get_state_api_url(state: str) -> str:
    """Get API URL for a state"""
    urls = {
        'CA': 'https://data.californiagovernment.org/resource',
        'NY': 'https://data.cityofnewyork.us',
        'IL': 'https://data.cityofchicago.org',
        # Add more states
    }
    return urls.get(state.upper(), '')
