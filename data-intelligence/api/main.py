"""FastAPI application for data intelligence services"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from harvesters.state_harvesters import get_harvester, InspectionRecord
from harvesters.expanded_states import EXPANDED_HARVESTER_REGISTRY, get_expanded_harvester
from harvesters.foia_automation import FOIAAutomation
from harvesters.business_registry import BusinessRegistryCorrelator
from harvesters.social_monitor import SocialReviewMonitor
from harvesters.competitor_monitor import CompetitorMonitor
from processors.risk_scorer import RiskScoringEngine, LeadScoringEngine
from analytics.predictive_models import PredictiveAnalyticsEngine, CompetitorIntelligence
from processors.real_time_monitor import RealTimeMonitoringEngine, AlertSeverity

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="HealthGuard Data Intelligence API",
    description="Public health data harvesting and predictive analytics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
risk_engine = RiskScoringEngine()
lead_engine = LeadScoringEngine()
predictive_engine = PredictiveAnalyticsEngine()
competitor_intel = CompetitorIntelligence()


# Pydantic models
class RestaurantSearchRequest(BaseModel):
    name: str
    city: Optional[str] = None
    state: Optional[str] = None


class RiskScoreRequest(BaseModel):
    restaurant_id: str
    inspection_records: List[Dict]


class LeadScoreRequest(BaseModel):
    restaurant_data: Dict
    public_inspection_data: Optional[List[Dict]] = None


class InspectionPredictionRequest(BaseModel):
    restaurant_id: str
    inspection_history: List[Dict]


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engines": {
            "risk_scoring": "active",
            "lead_scoring": "active",
            "predictive_analytics": "active",
            "competitor_intelligence": "active"
        }
    }


# Data harvesting endpoints
@app.post("/api/v1/harvest/search")
async def search_restaurants(request: RestaurantSearchRequest):
    """Search for restaurants across public health databases"""
    try:
        logger.info(f"Searching for restaurant: {request.name} in {request.state or 'all states'}")

        # This would call the actual harvester
        # For now, return mock data
        results = []

        return {
            "count": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Error searching restaurants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/harvest/states")
async def get_supported_states():
    """Get list of supported states for data harvesting"""
    return {
        "states": [
            {"code": "CA", "name": "California", "coverage": "100%", "last_updated": "2024-01-15"},
            {"code": "NY", "name": "New York", "coverage": "95%", "last_updated": "2024-01-14"},
            {"code": "IL", "name": "Illinois", "coverage": "90%", "last_updated": "2024-01-13"},
            # Add more states
        ],
        "total_restaurants": 750000,
        "coverage_percentage": 65
    }


# Risk scoring endpoints
@app.post("/api/v1/analytics/risk-score")
async def calculate_risk_score(request: RiskScoreRequest):
    """Calculate risk score for a restaurant"""
    try:
        score = risk_engine.calculate_risk_score(request.inspection_records)

        return {
            "restaurant_id": request.restaurant_id,
            "risk_score": {
                "overall": score.overall_score,
                "inspection_risk": score.inspection_risk,
                "violation_risk": score.violation_risk,
                "historical_risk": score.historical_risk,
                "financial_risk": score.financial_risk,
            },
            "confidence": score.confidence,
            "factors": score.factors,
            "recommendations": score.recommendations,
            "calculated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error calculating risk score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Lead scoring endpoints
@app.post("/api/v1/analytics/lead-score")
async def calculate_lead_score(request: LeadScoreRequest):
    """Calculate lead score for sales targeting"""
    try:
        score = lead_engine.calculate_lead_score(
            request.restaurant_data,
            request.public_inspection_data
        )

        return {
            "restaurant_id": request.restaurant_data.get('id', ''),
            "lead_score": score,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error calculating lead score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Predictive analytics endpoints
@app.post("/api/v1/analytics/predict-inspection")
async def predict_next_inspection(request: InspectionPredictionRequest):
    """Predict next health inspection"""
    try:
        prediction = predictive_engine.predict_next_inspection(request.inspection_history)

        return {
            "restaurant_id": request.restaurant_id,
            "prediction": {
                "predicted_date": prediction.predicted_date.isoformat(),
                "predicted_score": prediction.predicted_score,
                "confidence": prediction.confidence,
                "risk_factors": prediction.risk_factors,
                "recommendations": prediction.recommendations,
            },
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error predicting inspection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analytics/financial-impact")
async def predict_financial_impact(request: InspectionPredictionRequest):
    """Predict financial impact of compliance issues"""
    try:
        impact = predictive_engine.predict_financial_impact(
            request.inspection_history,
            request.seats if hasattr(request, 'seats') else 50
        )

        return {
            "restaurant_id": request.restaurant_id,
            "financial_impact": impact,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error predicting financial impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Sales enablement endpoints
@app.post("/api/v1/sales/generate-outreach")
async def generate_outreach_package(request: LeadScoreRequest):
    """Generate personalized outreach package"""
    try:
        # Calculate lead score
        lead_score = lead_engine.calculate_lead_score(
            request.restaurant_data,
            request.public_inspection_data
        )

        # Get predictive analytics
        prediction = None
        if request.public_inspection_data:
            prediction = predictive_engine.predict_next_inspection(request.public_inspection_data)

        # Generate package
        package = {
            "restaurant": {
                "name": request.restaurant_data.get('name'),
                "address": request.restaurant_data.get('address'),
                "city": request.restaurant_data.get('city'),
                "state": request.restaurant_data.get('state'),
            },
            "lead_score": lead_score,
            "value_proposition": generate_value_proposition(lead_score, prediction),
            "talking_points": lead_score.get('talking_points', []),
            "recommended_approach": lead_score.get('recommended_approach'),
            "email_templates": generate_email_templates(lead_score),
            "call_script": generate_call_script(lead_score),
        }

        return package

    except Exception as e:
        logger.error(f"Error generating outreach package: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def generate_value_proposition(lead_score: Dict, prediction: Dict = None) -> str:
    """Generate value proposition"""
    risk = lead_score.get('healthguard_risk', 50)
    competitor_gap = lead_score.get('competitor_gap', 0)

    if risk > 70:
        return f"Prevent costly health inspection failures and fines with automated monitoring"
    elif risk > 40:
        return f"Improve your health inspection scores and reduce compliance risk"
    else:
        return f"Maintain your excellent compliance record with automated monitoring"


def generate_email_templates(lead_score: Dict) -> Dict[str, str]:
    """Generate email templates"""
    name = lead_score.get('restaurant_name', '[Restaurant Name]')
    risk = lead_score.get('healthguard_risk', 50)

    if risk > 70:
        subject = f"Urgent: {name} health inspection compliance"
        body = f"""Hi,

I noticed {name} recently had some compliance issues on your health inspection.

Our automated monitoring system could have prevented these violations. Our customers typically see:
- 15-20 point improvement in inspection scores
- 60% reduction in violations
- 95% maintain 90+ scores within 6 months

Can we schedule a 15-minute call to discuss how we can help?

Best regards"""
    else:
        subject = f"Automated compliance monitoring for {name}"
        body = f"""Hi,

I wanted to reach out about HealthGuard's automated compliance monitoring system.

We help restaurants like {name}:
- Maintain 90+ inspection scores
- Eliminate manual temperature logging
- Receive real-time alerts for issues

Would you be interested in a quick demo?

Best regards"""

    return {
        "subject": subject,
        "body": body
    }


def generate_call_script(lead_score: Dict) -> Dict:
    """Generate sales call script"""
    risk = lead_score.get('healthguard_risk', 50)

    return {
        "opening": f"Hi, I'm calling from HealthGuard. I help restaurants automate their health compliance monitoring. Do you have 30 seconds?",
        "value_prop": lead_score.get('talking_points', [''])[0],
        "qualification": "How do you currently track food temperatures and compliance?",
        "next_steps": "I'd love to show you how it works. Are you available Tuesday or Thursday for a 15-minute demo?",
    }


# Background task endpoints
@app.post("/api/v1/tasks/harvest-state/{state}")
async def harvest_state_data(
    state: str,
    background_tasks: BackgroundTasks,
    days_back: int = Query(default=7, ge=1, le=365)
):
    """Trigger background harvest task for a state"""
    try:
        # Add to background tasks
        background_tasks.add_task(harvest_state_task, state, days_back)

        return {
            "status": "started",
            "message": f"Harvesting {state} data for last {days_back} days",
            "estimated_completion": f"{datetime.now() + timedelta(minutes=10)}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def harvest_state_task(state: str, days_back: int):
    """Background task for harvesting state data"""
    logger.info(f"Starting harvest task for {state}")
    # Implementation would call the actual harvester
    logger.info(f"Completed harvest task for {state}")


# ============================================
# ENHANCED DATA INTELLIGENCE ENDPOINTS
# ============================================

# FOIA Automation endpoints
@app.post("/api/v1/foia/generate-request")
async def generate_foia_request(
    state: str,
    agency_name: str,
    requester_info: Dict
):
    """Generate FOIA request for a jurisdiction"""
    try:
        foia_system = FOIAAutomation(config={})
        request = foia_system.generate_foia_request(
            jurisdiction=state,
            agency_name=agency_name,
            date_range=(
                datetime.now() - timedelta(days=365),
                datetime.now()
            ),
            requester_info=requester_info
        )

        return {
            "request_id": request.request_id,
            "status": request.status,
            "letter": request.notes,
            "expected_delivery": request.expected_delivery.isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating FOIA request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/foia/jurdictions")
async def get_foia_jurisdictions():
    """Get jurisdictions that may require FOIA requests"""
    try:
        foia_system = FOIAAutomation(config={})
        jurisdictions = foia_system.identify_jurisdictions_needing_foia()
        prioritized = foia_system.prioritize_foia_requests(jurisdictions)

        return {
            "jurisdictions": prioritized[:20],  # Top 20
            "total": len(prioritized)
        }
    except Exception as e:
        logger.error(f"Error getting FOIA jurisdictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/foia/batch-generate")
async def batch_generate_foia_requests(
    requester_info: Dict,
    batch_size: int = Query(default=5, ge=1, le=20)
):
    """Generate batch of FOIA requests"""
    try:
        foia_system = FOIAAutomation(config={})
        jurisdictions = foia_system.identify_jurisdictions_needing_foia()
        requests = foia_system.batch_generate_foia_requests(
            jurisdictions,
            requester_info,
            batch_size
        )

        return {
            "requests_generated": len(requests),
            "requests": [
                {
                    "jurisdiction": r.jurisdiction,
                    "agency": r.agency_name,
                    "status": r.status,
                    "letter": r.notes
                }
                for r in requests
            ]
        }
    except Exception as e:
        logger.error(f"Error generating batch FOIA requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Business Registry endpoints
@app.post("/api/v1/business/correlate")
async def correlate_business(inspection_record: Dict):
    """Correlate inspection record with business registry data"""
    try:
        correlator = BusinessRegistryCorrelator(config={})
        business_record = await correlator.correlate_inspection_with_business(inspection_record)

        if not business_record:
            return {"found": False, "record": None}

        return {
            "found": True,
            "record": {
                "business_name": business_record.business_name,
                "legal_name": business_record.legal_name,
                "ein": business_record.ein,
                "business_license": business_record.business_license,
                "health_permit": business_record.health_permit,
                "owners": business_record.owners,
                "data_sources": business_record.data_sources,
                "confidence_score": business_record.confidence_score
            }
        }
    except Exception as e:
        logger.error(f"Error correlating business: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/business/related")
async def find_related_businesses(business_name: str, address: str):
    """Find related businesses (sister locations, franchises)"""
    try:
        correlator = BusinessRegistryCorrelator(config={})

        # Create mock business record
        from harvesters.business_registry import BusinessRecord
        business_record = BusinessRecord(
            business_name=business_name,
            legal_name=None,
            dba_names=[],
            address=address,
            city="",
            state="",
            zip_code="",
            phone=None,
            email=None,
            website=None,
            ein=None,
            tax_id=None,
            business_license=None,
            health_permit=None,
            owners=[],
            parent_company=None,
            data_sources=[],
            last_updated=datetime.now(),
            confidence_score=0.5
        )

        related = await correlator.find_related_businesses(business_record)
        chain_info = correlator.calculate_chain_indicator(business_record, related)

        return {
            "related_count": len(related),
            "chain_info": chain_info,
            "related_businesses": related[:10]  # Top 10
        }
    except Exception as e:
        logger.error(f"Error finding related businesses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Social Monitoring endpoints
@app.post("/api/v1/social/monitor")
async def monitor_restaurant_social(
    restaurant_name: str,
    address: str,
    days_back: int = Query(default=30, ge=1, le=90)
):
    """Monitor social reviews for compliance mentions"""
    try:
        monitor = SocialReviewMonitor(config={})
        mentions = await monitor.monitor_restaurant_reviews(
            restaurant_name=restaurant_name,
            address=address,
            days_back=days_back
        )

        alert = await monitor.generate_compliance_alert(mentions)

        return {
            "mentions_found": len(mentions),
            "compliance_mentions": [m.compliance_mentions for m in mentions],
            "alert": alert
        }
    except Exception as e:
        logger.error(f"Error monitoring social reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/social/batch-monitor")
async def batch_monitor_social(
    restaurants: List[Dict],
    days_back: int = Query(default=30, ge=1, le=90)
):
    """Monitor multiple restaurants for social compliance mentions"""
    try:
        monitor = SocialReviewMonitor(config={})
        alerts = await monitor.batch_monitor_restaurants(restaurants, days_back)

        return {
            "restaurants_monitored": len(restaurants),
            "alerts_generated": len(alerts),
            "alerts": list(alerts.values())
        }
    except Exception as e:
        logger.error(f"Error in batch social monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Competitor Monitoring endpoints
@app.post("/api/v1/competitor/detect")
async def detect_competitor_installations(
    territory: Dict,
    sources: Optional[List[str]] = None
):
    """Detect competitor installations in a territory"""
    try:
        monitor = CompetitorMonitor(config={})
        installations = await monitor.detect_competitor_installations(
            territory,
            sources or ['job_postings', 'reviews', 'business_licenses']
        )

        return {
            "territory": f"{territory.get('city', territory['state'])}",
            "installations_detected": len(installations),
            "installations": [
                {
                    "competitor": i.competitor_name,
                    "restaurant": i.restaurant_name,
                    "address": i.address,
                    "confidence": i.confidence_score,
                    "detection_method": i.detection_method
                }
                for i in installations
            ]
        }
    except Exception as e:
        logger.error(f"Error detecting competitor installations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/competitor/market-intelligence")
async def get_market_intelligence(territory: Dict):
    """Get market penetration and competitive intelligence"""
    try:
        monitor = CompetitorMonitor(config={})
        intelligence = await monitor.calculate_market_penetration(territory)

        return {
            "territory": f"{intelligence.city}, {intelligence.state}" if intelligence.city else intelligence.state,
            "total_restaurants": intelligence.total_restaurants,
            "penetration_rate": intelligence.competitor_penetration,
            "market_saturation": intelligence.market_saturation,
            "competitor_shares": intelligence.competitor_market_shares,
            "available_market": intelligence.available_market
        }
    except Exception as e:
        logger.error(f"Error getting market intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/competitor/vulnerability")
async def assess_competitive_vulnerability(
    territory: Dict,
    restaurant: Dict
):
    """Assess vulnerability for competitor displacement"""
    try:
        monitor = CompetitorMonitor(config={})
        intelligence = await monitor.calculate_market_penetration(territory)
        vulnerability = monitor.identify_competitive_vulnerability(intelligence, restaurant)

        return vulnerability
    except Exception as e:
        logger.error(f"Error assessing competitive vulnerability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/competitor/competitive-intelligence")
async def generate_competitive_intelligence_report(
    territories: List[Dict]
):
    """Generate comprehensive competitive intelligence report"""
    try:
        monitor = CompetitorMonitor(config={})
        report = await monitor.generate_competitive_intelligence_report(territories)

        return report
    except Exception as e:
        logger.error(f"Error generating competitive intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Real-time Monitoring endpoints
@app.post("/api/v1/monitoring/start")
async def start_real_time_monitoring(
    territories: List[Dict],
    background_tasks: BackgroundTasks
):
    """Start real-time monitoring for territories"""
    try:
        monitoring_engine = RealTimeMonitoringEngine(config={})

        # Start monitoring in background
        background_tasks.add_task(
            monitoring_engine.start_monitoring,
            territories,
            lambda alert: logger.info(f"Alert: {alert.title}")
        )

        return {
            "status": "started",
            "territories": len(territories),
            "message": "Real-time monitoring started"
        }
    except Exception as e:
        logger.error(f"Error starting real-time monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/monitoring/daily-summary")
async def get_daily_summary(
    state: str,
    city: Optional[str] = None
):
    """Get daily monitoring summary"""
    try:
        monitoring_engine = RealTimeMonitoringEngine(config={})
        territories = [{"state": state, "city": city} if city else {"state": state}]
        summary = await monitoring_engine.generate_daily_summary(territories)

        return summary
    except Exception as e:
        logger.error(f"Error generating daily summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced State Harvesting endpoints
@app.get("/api/v1/harvest/states-expanded")
async def get_expanded_supported_states():
    """Get list of all supported states (expanded)"""
    return {
        "states": [
            {"code": code, "name": code, "coverage": "varies", "harvester": cls.__name__}
            for code, cls in EXPANDED_HARVESTER_REGISTRY.items()
        ],
        "total_states": len(EXPANDED_HARVESTER_REGISTRY),
        "coverage_percentage": 95
    }


@app.post("/api/v1/harvest/harvest-state/{state}")
async def harvest_state_data_expanded(
    state: str,
    days_back: int = Query(default=7, ge=1, le=365)
):
    """Harvest data for a specific state using expanded harvesters"""
    try:
        from harvesters.expanded_states import get_expanded_harvester

        harvester = get_expanded_harvester(state, config={})
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        records = await harvester.harvest(start_date, end_date)

        return {
            "state": state,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "records_harvested": len(records),
            "records": [
                {
                    "restaurant_name": r.restaurant_name,
                    "address": r.address,
                    "city": r.city,
                    "inspection_date": r.inspection_date.isoformat(),
                    "score": r.score,
                    "grade": r.grade,
                    "violations": len(r.violations)
                }
                for r in records[:100]  # Limit response
            ]
        }
    except Exception as e:
        logger.error(f"Error harvesting state data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced analytics endpoints
@app.post("/api/v1/analytics/compliance-trend")
async def analyze_compliance_trend(
    restaurant_id: str,
    inspection_records: List[Dict]
):
    """Analyze compliance trends over time"""
    try:
        # Sort by date
        sorted_records = sorted(
            inspection_records,
            key=lambda x: x.get('inspection_date', '')
        )

        if not sorted_records:
            return {"trend": "insufficient_data"}

        # Calculate trend
        scores = [r.get('score', 0) for r in sorted_records if r.get('score')]

        if len(scores) < 2:
            return {"trend": "insufficient_data"}

        # Simple trend analysis
        recent_avg = sum(scores[-3:]) / min(3, len(scores))
        older_avg = sum(scores[:-3]) / max(1, len(scores) - 3)

        trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        change = recent_avg - older_avg

        return {
            "trend": trend,
            "change_points": round(change, 1),
            "recent_average": round(recent_avg, 1),
            "historical_average": round(older_avg, 1),
            "data_points": len(scores)
        }
    except Exception as e:
        logger.error(f"Error analyzing compliance trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analytics/violation-patterns")
async def analyze_violation_patterns(
    inspection_records: List[Dict]
):
    """Analyze violation patterns across inspections"""
    try:
        # Aggregate violations
        violation_counts = {}
        category_counts = {}

        for record in inspection_records:
            for violation in record.get('violations', []):
                category = violation.get('category', 'other')
                category_counts[category] = category_counts.get(category, 0) + 1

                # Count specific violations
                code = violation.get('code', '')
                if code:
                    violation_counts[code] = violation_counts.get(code, 0) + 1

        # Get top violations
        top_violations = sorted(
            violation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        top_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "total_violations": sum(violation_counts.values()),
            "top_violations": [
                {"code": code, "count": count}
                for code, count in top_violations
            ],
            "categories": [
                {"category": cat, "count": count}
                for cat, count in top_categories
            ]
        }
    except Exception as e:
        logger.error(f"Error analyzing violation patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
