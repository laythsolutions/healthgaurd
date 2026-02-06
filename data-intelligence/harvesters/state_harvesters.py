"""State-specific health department harvesters"""

import logging
from datetime import datetime, timedelta
from typing import List
from urllib.parse import quote

from .base import APIHarvester, ScraperHarvester, InspectionRecord

logger = logging.getLogger(__name__)


class CaliforniaHealthHarvester(APIHarvester):
    """California Retail Food Inspection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest California food inspection data"""
        records = []

        # California Open Data Portal
        url = f"{self.base_url}/resource/ff9s-5k4m.json"

        try:
            data = await self._fetch(url)

            for item in data:
                # Parse inspection date
                inspection_date = self._parse_date(item.get('inspection_date'))

                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('facility_name', ''),
                        address=item.get('facility_address', ''),
                        city=item.get('facility_city', ''),
                        state='CA',
                        zip_code=item.get('facility_zip', ''),
                        inspection_date=inspection_date,
                        score=item.get('inspection_score'),
                        grade=item.get('grade'),
                        violations=self._parse_violations(item.get('violations', [])),
                        risk_level=item.get('risk_level', 'unknown'),
                        facility_type=item.get('facility_type', 'Restaurant'),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from California")
            return records

        except Exception as e:
            logger.error(f"Error harvesting California data: {e}")
            return []

    async def search_by_name(self, name: str, city: str = None) -> List[InspectionRecord]:
        """Search California restaurants by name"""
        url = f"{self.base_url}/resource/ff9s-5k4m.json"
        params = {'facility_name': name}

        if city:
            params['facility_city'] = city

        try:
            data = await self._fetch(url, params=params)
            records = []

            for item in data:
                record = InspectionRecord(
                    restaurant_name=item.get('facility_name', ''),
                    address=item.get('facility_address', ''),
                    city=item.get('facility_city', ''),
                    state='CA',
                    zip_code=item.get('facility_zip', ''),
                    inspection_date=self._parse_date(item.get('inspection_date')),
                    score=item.get('inspection_score'),
                    grade=item.get('grade'),
                    violations=self._parse_violations(item.get('violations', [])),
                    raw_data=item
                )
                records.append(record)

            return records

        except Exception as e:
            logger.error(f"Error searching California data: {e}")
            return []

    async def search_by_address(self, address: str) -> List[InspectionRecord]:
        """Search California restaurants by address"""
        # Similar to search_by_name
        return await self.search_by_name(address)

    def _parse_date(self, date_str: str) -> datetime:
        """Parse California date format"""
        if not date_str:
            return datetime.now()

        try:
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        except:
            return datetime.now()

    def _parse_violations(self, raw_violations: List) -> List[dict]:
        """Parse California violation format"""
        violations = []

        for v in raw_violations:
            violations.append({
                'code': v.get('violation_code', ''),
                'description': v.get('description', ''),
                'severity': v.get('severity', 'unknown'),
                'category': v.get('category', 'other')
            })

        return violations


class NYCHealthHarvester(ScraperHarvester):
    """New York City Restaurant Inspection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest NYC restaurant inspection data"""
        # NYC DOHMH uses a different API
        url = f"{self.base_url}/api/views/43nn-pn8j/rows.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data.get('data', []):
                inspection_date = self._parse_date(item[8])  # Date field

                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item[0],  # DBA (doing business as)
                        address=item[3],  # Building + street
                        city='New York',
                        borough=item[1],
                        state='NY',
                        zip_code=str(item[4]),  # ZIP code
                        inspection_date=inspection_date,
                        score=item[12] if len(item) > 12 else None,  # Score
                        violations=self._parse_violations(item[10] if len(item) > 10 else ''),
                        grade=item[14] if len(item) > 14 else None,  # Grade
                        facility_type=item[2] if len(item) > 2 else 'Restaurant',
                        raw_data={'raw': item}
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from NYC")
            return records

        except Exception as e:
            logger.error(f"Error harvesting NYC data: {e}")
            return []

    async def search_by_name(self, name: str, city: str = None) -> List[InspectionRecord]:
        """Search NYC restaurants by name"""
        url = f"{self.base_url}/api/views/43nn-pn8j/rows.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data.get('data', []):
                if name.lower() in item[0].lower():
                    record = InspectionRecord(
                        restaurant_name=item[0],
                        address=item[3],
                        city='New York',
                        borough=item[1],
                        state='NY',
                        zip_code=str(item[4]),
                        inspection_date=self._parse_date(item[8]),
                        score=item[12] if len(item) > 12 else None,
                        violations=self._parse_violations(item[10] if len(item) > 10 else ''),
                        grade=item[14] if len(item) > 14 else None,
                        raw_data={'raw': item}
                    )
                    records.append(record)

            return records

        except Exception as e:
            logger.error(f"Error searching NYC data: {e}")
            return []

    async def search_by_address(self, address: str) -> List[InspectionRecord]:
        """Search NYC restaurants by address"""
        # Similar implementation
        return await self.search_by_name(address)

    def _parse_date(self, date_str: str) -> datetime:
        """Parse NYC date format"""
        if not date_str:
            return datetime.now()

        try:
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        except:
            return datetime.now()

    def _parse_violations(self, violation_str: str) -> List[dict]:
        """Parse NYC violation string format"""
        if not violation_str:
            return []

        violations = []
        # NYC violations are semicolon-separated
        for v in violation_str.split(';'):
            if v.strip():
                violations.append({
                    'code': '',
                    'description': v.strip(),
                    'severity': 'unknown',
                    'category': 'other'
                })

        return violations


class ChicagoHealthHarvester(APIHarvester):
    """Chicago Food Protection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Chicago food inspection data"""
        url = f"{self.base_url}/resource/4ijn-s7e5.json"

        try:
            # Chicago API uses SOQL for filtering
            params = {
                '$where': f"inspection_date between '{start_date.strftime('%Y-%m-%d')}' and '{end_date.strftime('%Y-%m-%d')}'",
                '$limit': 50000
            }

            data = await self._fetch(url, params=params)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))

                record = InspectionRecord(
                    restaurant_name=item.get('aka_name', item.get('dba_name', '')),
                    address=item.get('address', ''),
                    city='Chicago',
                    state='IL',
                    zip_code=item.get('zip', ''),
                    inspection_date=inspection_date,
                    score=item.get('inspection_score'),
                    violations=self._parse_violations(item.get('violations', '')),
                    risk_level=item.get('risk', 'unknown'),
                    facility_type=item.get('facility_type', 'Restaurant'),
                    inspector_name=item.get('inspection_type'),
                    raw_data=item
                )
                records.append(record)

            logger.info(f"Harvested {len(records)} records from Chicago")
            return records

        except Exception as e:
            logger.error(f"Error harvesting Chicago data: {e}")
            return []

    async def search_by_name(self, name: str, city: str = None) -> List[InspectionRecord]:
        """Search Chicago restaurants by name"""
        url = f"{self.base_url}/resource/4ijn-s7e5.json"

        params = {
            '$where': f"lower(aka_name) like lower('%{name}%')",
            '$limit': 1000
        }

        try:
            data = await self._fetch(url, params=params)
            records = []

            for item in data:
                record = InspectionRecord(
                    restaurant_name=item.get('aka_name', ''),
                    address=item.get('address', ''),
                    city='Chicago',
                    state='IL',
                    zip_code=item.get('zip', ''),
                    inspection_date=self._parse_date(item.get('inspection_date')),
                    score=item.get('inspection_score'),
                    violations=self._parse_violations(item.get('violations', '')),
                    raw_data=item
                )
                records.append(record)

            return records

        except Exception as e:
            logger.error(f"Error searching Chicago data: {e}")
            return []

    async def search_by_address(self, address: str) -> List[InspectionRecord]:
        """Search Chicago restaurants by address"""
        return await self.search_by_name(address)

    def _parse_date(self, date_str: str) -> datetime:
        """Parse Chicago date format"""
        if not date_str:
            return datetime.now()

        try:
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
        except:
            try:
                return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
            except:
                return datetime.now()

    def _parse_violations(self, violation_str: str) -> List[dict]:
        """Parse Chicago violation string format"""
        if not violation_str:
            return []

        violations = []
        # Chicago violations are pipe-separated comments
        for v in violation_str.split('|'):
            if v.strip():
                violations.append({
                    'code': '',
                    'description': v.strip(),
                    'severity': 'unknown',
                    'category': 'other'
                })

        return violations


# Create registry of harvesters
HARVESTER_REGISTRY = {
    'CA': CaliforniaHealthHarvester,
    'NYC': NYCHealthHarvester,
    'IL': ChicagoHealthHarvester,
    # Add more state harvesters here
}


def get_harvester(state: str, config: dict) -> BaseHarvester:
    """Get harvester for a state"""
    harvester_class = HARVESTER_REGISTRY.get(state.upper())

    if not harvester_class:
        logger.warning(f"No harvester found for {state}, using base scraper")
        # Return a generic scraper
        return ScraperHarvester(config)

    return harvester_class(config)
