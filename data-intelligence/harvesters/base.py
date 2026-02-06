"""Base classes for data harvesters"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass

from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class InspectionRecord:
    """Standardized inspection record"""
    restaurant_name: str
    address: str
    city: str
    state: str
    zip_code: str
    inspection_date: datetime
    score: Optional[int] = None
    violations: List[Dict] = None
    risk_level: Optional[str] = None
    inspector_name: Optional[str] = None
    facility_type: Optional[str] = None
    raw_data: Dict = None

    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.raw_data is None:
            self.raw_data = {}


class BaseHarvester(ABC):
    """Base class for all data harvesters"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.state = config.get('state', '')
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(f"harvesters.{self.name}")

    @abstractmethod
    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest inspection data for date range"""
        pass

    @abstractmethod
    async def search_by_name(self, name: str, city: str = None) -> List[InspectionRecord]:
        """Search for restaurants by name"""
        pass

    @abstractmethod
    async def search_by_address(self, address: str) -> List[InspectionRecord]:
        """Search for restaurants by address"""
        pass

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _fetch(self, url: str, **kwargs) -> Any:
        """Fetch data with retry logic"""
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, **kwargs)
            response.raise_for_status()
            return response.json()

    def normalize_violations(self, raw_violations: List) -> List[Dict]:
        """Normalize violations to standard format"""
        normalized = []

        for violation in raw_violations:
            normalized.append({
                'code': violation.get('code', ''),
                'description': violation.get('description', ''),
                'severity': violation.get('severity', 'unknown'),
                'category': violation.get('category', 'other'),
            })

        return normalized

    def calculate_risk_level(self, score: Optional[int], violations: List[Dict]) -> str:
        """Calculate risk level from score and violations"""
        if score is not None:
            if score >= 90:
                return 'low'
            elif score >= 70:
                return 'medium'
            else:
                return 'high'

        # If no score, use violation count and severity
        critical_violations = sum(1 for v in violations if v.get('severity') == 'critical')

        if critical_violations > 0:
            return 'high'
        elif len(violations) > 5:
            return 'medium'
        else:
            return 'low'


class APIHarvester(BaseHarvester):
    """Base class for API-based harvesters"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')
        self.rate_limit = config.get('rate_limit', 100)  # requests per minute


class ScraperHarvester(BaseHarvester):
    """Base class for web scraping harvesters"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url')
        self.use_selenium = config.get('use_selenium', False)

    async def _fetch_page(self, url: str) -> str:
        """Fetch HTML page"""
        import httpx

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def _parse_html(self, html: str):
        """Parse HTML with BeautifulSoup"""
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, 'lxml')


class FOIAHarvester(BaseHarvester):
    """Base class for FOIA-based harvesters"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.foia_contact = config.get('foia_contact')
        self.foia_email = config.get('foia_email')

    async def submit_foia_request(self, request_details: Dict) -> Dict:
        """Submit automated FOIA request"""
        # Implementation varies by jurisdiction
        raise NotImplementedError
