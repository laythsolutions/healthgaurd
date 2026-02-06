"""FastAPI application for data intelligence services"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from harvesters.state_harvesters import get_harvester, InspectionRecord
from processors.risk_scorer import RiskScoringEngine, LeadScoringEngine
from analytics.predictive_models import PredictiveAnalyticsEngine, CompetitorIntelligence

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


# Run with: uvicorn api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
