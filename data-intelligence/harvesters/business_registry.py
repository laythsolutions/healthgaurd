"""
Business Registry Correlation System

Correlates public health inspection data with business registries,
license databases, and corporate records to enhance data quality
and enable advanced analytics.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import json
import re

logger = logging.getLogger(__name__)


@dataclass
class BusinessRecord:
    """Unified business record from multiple sources"""
    business_name: str
    legal_name: Optional[str]
    dba_names: List[str]
    address: str
    city: str
    state: str
    zip_code: str
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]

    # Business identifiers
    ein: Optional[str]
    tax_id: Optional[str]
    business_license: Optional[str]
    health_permit: Optional[str]

    # Ownership
    owners: List[dict]
    parent_company: Optional[str]

    # Metadata
    data_sources: List[str]
    last_updated: datetime
    confidence_score: float


class BusinessRegistryCorrelator:
    """Correlates inspection data with business registries"""

    def __init__(self, config: dict):
        self.config = config
        self.match_threshold = 0.85
        self.business_cache = {}

    async def correlate_inspection_with_business(
        self,
        inspection_record: dict
    ) -> Optional[BusinessRecord]:
        """
        Correlate a health inspection record with business registry data

        Sources queried:
        1. Secretary of State business entities
        2. Local business license databases
        3. Health department permits
        4. Corporate registries (Dun & Bradstreet, etc.)
        """

        # Extract key identifiers
        business_name = inspection_record.get('restaurant_name', '')
        address = inspection_record.get('address', '')
        city = inspection_record.get('city', '')
        state = inspection_record.get('state', '')
        zip_code = inspection_record.get('zip_code', '')

        # Check cache first
        cache_key = f"{state}:{city}:{business_name}"
        if cache_key in self.business_cache:
            return self.business_cache[cache_key]

        # Query multiple sources
        corporate_records = await self._query_corporate_registry(business_name, state)
        license_records = await self._query_business_license(city, state, business_name)
        permit_records = await self._query_health_permit(business_name, city, state)

        # Merge records using fuzzy matching
        merged_record = self._merge_business_records(
            inspection_record,
            corporate_records,
            license_records,
            permit_records
        )

        # Cache the result
        if merged_record:
            self.business_cache[cache_key] = merged_record

        return merged_record

    async def _query_corporate_registry(
        self,
        business_name: str,
        state: str
    ) -> List[dict]:
        """Query Secretary of State business entity database"""

        # In production, this would call state-specific APIs
        # For now, return mock data structure

        return [
            {
                'legal_name': business_name,
                'entity_type': 'LLC',
                'status': 'Active',
                'registration_date': '2015-06-15',
                'ein': 'XX-XXXXXXX',
                'registered_agent': 'Registered Agent Services Inc',
                'principals': [
                    {'name': 'John Owner', 'title': 'Member', 'ownership_pct': 100}
                ]
            }
        ]

    async def _query_business_license(
        self,
        city: str,
        state: str,
        business_name: str
    ) -> List[dict]:
        """Query local business license database"""

        # In production, query city/county business license portal
        return [
            {
                'license_number': f'{city.upper()}-{state}-BL-{2024}-{12345}',
                'license_type': 'Restaurant',
                'license_status': 'Active',
                'expiration_date': '2024-12-31',
                'business_category': 'Eating and Drinking Places',
                'employee_count': 15,
                'square_footage': 2500
            }
        ]

    async def _query_health_permit(
        self,
        business_name: str,
        city: str,
        state: str
    ) -> List[dict]:
        """Query health department permit database"""

        return [
            {
                'permit_number': f'HDP-{state}-{city[:3].upper()}-{12345}',
                'permit_type': 'Food Service Establishment',
                'permit_status': 'Active',
                'seating_capacity': 75,
                'food_service_type': 'Full Service',
                'risk_category': 'High Risk'
            }
        ]

    def _merge_business_records(
        self,
        inspection_record: dict,
        corporate_records: List[dict],
        license_records: List[dict],
        permit_records: List[dict]
    ) -> Optional[BusinessRecord]:
        """Merge records from multiple sources using confidence scoring"""

        if not any([corporate_records, license_records, permit_records]):
            return None

        # Start with inspection data
        base_record = BusinessRecord(
            business_name=inspection_record.get('restaurant_name', ''),
            legal_name=None,
            dba_names=[],
            address=inspection_record.get('address', ''),
            city=inspection_record.get('city', ''),
            state=inspection_record.get('state', ''),
            zip_code=inspection_record.get('zip_code', ''),
            phone=None,
            email=None,
            website=None,
            ein=None,
            tax_id=None,
            business_license=None,
            health_permit=None,
            owners=[],
            parent_company=None,
            data_sources=['inspection'],
            last_updated=datetime.now(),
            confidence_score=0.5
        )

        # Merge corporate data
        if corporate_records:
            corp = corporate_records[0]
            base_record.legal_name = corp.get('legal_name')
            base_record.ein = corp.get('ein')
            base_record.owners = corp.get('principals', [])
            base_record.data_sources.append('corporate_registry')
            base_record.confidence_score += 0.2

        # Merge license data
        if license_records:
            lic = license_records[0]
            base_record.business_license = lic.get('license_number')
            base_record.data_sources.append('business_license')
            base_record.confidence_score += 0.15

        # Merge permit data
        if permit_records:
            permit = permit_records[0]
            base_record.health_permit = permit.get('permit_number')
            base_record.data_sources.append('health_permit')
            base_record.confidence_score += 0.15

        return base_record

    async def find_related_businesses(
        self,
        business_record: BusinessRecord
    ) -> List[dict]:
        """
        Find related businesses using corporate relationships

        Returns:
            - Sister locations (same ownership)
            - Franchise locations
            - Former locations (same name, different ownership)
        """

        related = []

        # Find by EIN (same corporate entity)
        if business_record.ein:
            sister_locations = await self._find_by_ein(business_record.ein)
            related.extend(sister_locations)

        # Find by ownership
        for owner in business_record.owners:
            owner_businesses = await self._find_by_owner(owner.get('name'))
            related.extend(owner_businesses)

        # Find similar names (potential franchises)
        potential_franchises = await self._find_potential_franchises(
            business_record.business_name
        )
        related.extend(potential_franchises)

        return related

    async def _find_by_ein(self, ein: str) -> List[dict]:
        """Find all businesses with the same EIN"""
        # In production, query corporate registry by EIN
        return []

    async def _find_by_owner(self, owner_name: str) -> List[dict]:
        """Find all businesses owned by the same person/entity"""
        # In production, query corporate registry by owner
        return []

    async def _find_potential_franchises(self, business_name: str) -> List[dict]:
        """Find potential franchise locations by name similarity"""
        # In production, use fuzzy name matching
        return []

    def calculate_chain_indicator(
        self,
        business_record: BusinessRecord,
        related_businesses: List[dict]
    ) -> dict:
        """
        Determine if a business is part of a chain

        Returns:
            - is_chain: Boolean
            - chain_size: Number of locations
            - chain_type: 'franchise', 'corporate', 'family_owned', 'independent'
        """

        if len(related_businesses) >= 5:
            return {
                'is_chain': True,
                'chain_size': len(related_businesses),
                'chain_type': self._determine_chain_type(business_record, related_businesses)
            }

        return {
            'is_chain': False,
            'chain_size': 1,
            'chain_type': 'independent'
        }

    def _determine_chain_type(
        self,
        business_record: BusinessRecord,
        related_businesses: List[dict]
    ) -> str:
        """Determine the type of chain"""

        # Check if names vary significantly (franchise)
        names = [b.get('business_name', '') for b in related_businesses]
        name_variance = len(set(names)) / len(names)

        if name_variance > 0.3:
            return 'franchise'

        # Check for corporate ownership
        if business_record.parent_company:
            return 'corporate'

        # Check ownership structure
        if len(business_record.owners) <= 3:
            return 'family_owned'

        return 'corporate'

    async def enrich_with_business_intelligence(
        self,
        business_record: BusinessRecord
    ) -> dict:
        """
        Enrich business record with additional intelligence

        Includes:
        - Financial health indicators
        - Credit score estimates
        - Legal filings
        - Real estate ownership
        """

        intelligence = {
            'financial_health': await self._assess_financial_health(business_record),
            'credit_profile': await self._get_credit_profile(business_record),
            'legal_filings': await self._check_legal_filings(business_record),
            'real_estate': await self._check_real_estate_ownership(business_record),
            'market_position': await self._assess_market_position(business_record)
        }

        return intelligence

    async def _assess_financial_health(
        self,
        business_record: BusinessRecord
    ) -> dict:
        """Assess financial health using public indicators"""

        # In production, query business credit bureaus, financial statements
        return {
            'revenue_estimate': None,  # From employee count, industry benchmarks
            'profitability_estimate': None,  # From industry averages
            'growth_indicator': 'unknown',
            'risk_score': 50  # 0-100 scale
        }

    async def _get_credit_profile(
        self,
        business_record: BusinessRecord
    ) -> dict:
        """Get business credit profile"""

        return {
            'credit_score': None,  # From Dun & Bradstreet, etc.
            'payment_history': None,
            'liens': None,
            'judgments': None
        }

    async def _check_legal_filings(
        self,
        business_record: BusinessRecord
    ) -> List[dict]:
        """Check for lawsuits, bankruptcies, etc."""

        # In production, query court records
        return []

    async def _check_real_estate_ownership(
        self,
        business_record: BusinessRecord
    ) -> dict:
        """Check if business owns vs. leases property"""

        # In production, query property assessor records
        return {
            'owns_property': None,
            'property_value': None,
            'mortgage_liens': None
        }

    async def _assess_market_position(
        self,
        business_record: BusinessRecord
    ) -> dict:
        """Assess competitive position in local market"""

        return {
            'market_share_estimate': None,
            'competitor_count': None,
            'local_ranking': None
        }

    def fuzzy_match_business_names(
        self,
        name1: str,
        name2: str
    ) -> float:
        """
        Calculate similarity score between two business names

        Returns: 0.0 to 1.0
        """

        # Normalize names
        n1 = self._normalize_business_name(name1)
        n2 = self._normalize_business_name(name2)

        # Simple implementation (use Levenshtein in production)
        if n1 == n2:
            return 1.0

        # Check for partial matches
        if n1 in n2 or n2 in n1:
            return 0.7

        return 0.0

    def _normalize_business_name(self, name: str) -> str:
        """Normalize business name for comparison"""

        # Remove common suffixes/prefixes
        suffixes = ['LLC', 'Inc', 'Corp', 'Corporation', 'Ltd', 'Co', 'Company', 'Restaurant']
        for suffix in suffixes:
            name = name.replace(suffix, '').strip()

        # Convert to lowercase
        name = name.lower()

        # Remove special characters
        name = re.sub(r'[^a-z0-9\s]', '', name)

        # Remove extra whitespace
        name = ' '.join(name.split())

        return name

    async def batch_correlate(
        self,
        inspection_records: List[dict]
    ) -> Dict[str, BusinessRecord]:
        """Correlate multiple inspection records in batch"""

        results = {}
        for record in inspection_records:
            business_record = await self.correlate_inspection_with_business(record)
            if business_record:
                key = f"{record['state']}:{record['city']}:{record['restaurant_name']}"
                results[key] = business_record

        logger.info(f"Correlated {len(results)} of {len(inspection_records)} records")
        return results
