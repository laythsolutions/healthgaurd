"""
Expanded State Health Department Harvesters (47 additional states)

This module extends the data harvesting to cover all 50 US states plus
major municipalities with independent health departments.
"""

import logging
from datetime import datetime
from typing import List
from .base import APIHarvester, ScraperHarvester, InspectionRecord

logger = logging.getLogger(__name__)


class TexasHealthHarvester(APIHarvester):
    """Texas Food Establishment Inspection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Texas inspection data"""
        url = f"{self.base_url}/resource/tdt9-2kci.json"
        params = {
            '$where': f"inspection_date between '{start_date.strftime('%Y-%m-%d')}' and '{end_date.strftime('%Y-%m-%d')}'",
            '$limit': 50000
        }

        try:
            data = await self._fetch(url, params=params)
            records = []

            for item in data:
                record = InspectionRecord(
                    restaurant_name=item.get('restaurant_name', ''),
                    address=item.get('address', ''),
                    city=item.get('city', ''),
                    state='TX',
                    zip_code=item.get('zip', ''),
                    inspection_date=self._parse_date(item.get('inspection_date')),
                    score=item.get('score'),
                    grade=self._calculate_grade(item.get('score')),
                    violations=self._parse_violations(item.get('violations', '')),
                    facility_type=item.get('facility_type', 'Restaurant'),
                    raw_data=item
                )
                records.append(record)

            logger.info(f"Harvested {len(records)} records from Texas")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Texas data: {e}")
            return []


class FloridaHealthHarvester(APIHarvester):
    """Florida Restaurant Inspection Harvester - DBPR"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Florida inspection data"""
        url = f"{self.base_url}/resource/vfer-vgmb.json"
        params = {
            '$where': f"inspection_date between '{start_date.strftime('%Y-%m-%d')}' and '{end_date.strftime('%Y-%m-%d')}'",
            '$limit': 50000
        }

        try:
            data = await self._fetch(url, params=params)
            records = []

            for item in data:
                record = InspectionRecord(
                    restaurant_name=item.get('licensee_name', ''),
                    address=item.get('address', ''),
                    city=item.get('city', ''),
                    state='FL',
                    zip_code=item.get('zip_code', ''),
                    inspection_date=self._parse_date(item.get('inspection_date')),
                    violations=self._parse_violations(item.get('inspection_results', '')),
                    facility_type=item.get('license_category', 'Restaurant'),
                    raw_data=item
                )
                records.append(record)

            logger.info(f"Harvested {len(records)} records from Florida")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Florida data: {e}")
            return []


class PennsylvaniaHealthHarvester(APIHarvester):
    """Pennsylvania Food Safety Inspection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Pennsylvania inspection data"""
        url = f"{self.base_url}/resource/pqk4-nqwq.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('name', ''),
                        address=item.get('address', ''),
                        city=item.get('city', ''),
                        state='PA',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violations', '')),
                        facility_type=item.get('category', 'Restaurant'),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Pennsylvania")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Pennsylvania data: {e}")
            return []


class OhioHealthHarvester(APIHarvester):
    """Ohio Food Service Inspection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Ohio inspection data"""
        url = f"{self.base_url}/resource/cnrg-2y8w.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('business_name', ''),
                        address=item.get('address', ''),
                        city=item.get('city', ''),
                        state='OH',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violations', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Ohio")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Ohio data: {e}")
            return []


class GeorgiaHealthHarvester(APIHarvester):
    """Georgia Restaurant Inspection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Georgia inspection data"""
        url = f"{self.base_url}/resource/kyda-fcvf.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('date(inspection)'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('facility_name', ''),
                        address=item.get('street_address', ''),
                        city=item.get('city', ''),
                        state='GA',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        score=item.get('inspection_score'),
                        grade=item.get('grade'),
                        violations=self._parse_violations(item.get('violations', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Georgia")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Georgia data: {e}")
            return []


class NorthCarolinaHealthHarvester(APIHarvester):
    """North Carolina Food Inspection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest North Carolina inspection data"""
        url = f"{self.base_url}/resource/ntk4-x6pj.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspectdate'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('name', ''),
                        address=item.get('address', ''),
                        city=item.get('city', ''),
                        state='NC',
                        zip_code=item.get('zipcode', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('comments', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from North Carolina")
            return records
        except Exception as e:
            logger.error(f"Error harvesting North Carolina data: {e}")
            return []


class MichiganHealthHarvester(APIHarvester):
    """Michigan Food Establishment Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Michigan inspection data"""
        url = f"{self.base_url}/resource/2pjd-8m2h.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('name', ''),
                        address=item.get('address', ''),
                        city=item.get('city', ''),
                        state='MI',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violation', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Michigan")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Michigan data: {e}")
            return []


class NewJerseyHealthHarvester(APIHarvester):
    """New Jersey Retail Food Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest New Jersey inspection data"""
        url = f"{self.base_url}/resource/xjsd-x68q.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspectiondate'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('facility_name', ''),
                        address=item.get('street_address', ''),
                        city=item.get('city', ''),
                        state='NJ',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violations', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from New Jersey")
            return records
        except Exception as e:
            logger.error(f"Error harvesting New Jersey data: {e}")
            return []


class VirginiaHealthHarvester(APIHarvester):
    """Virginia Food Establishment Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Virginia inspection data"""
        url = f"{self.base_url}/resource/vxzf-iikp.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('facility_name', ''),
                        address=item.get('address', ''),
                        city=item.get('city', ''),
                        state='VA',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violations', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Virginia")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Virginia data: {e}")
            return []


class WashingtonHealthHarvester(APIHarvester):
    """Washington State Food Safety Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Washington inspection data"""
        url = f"{self.base_url}/resource/gqk3-i598.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('name', ''),
                        address=item.get('address', ''),
                        city=item.get('city', ''),
                        state='WA',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violation_desc', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Washington")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Washington data: {e}")
            return []


class ArizonaHealthHarvester(APIHarvester):
    """Arizona Food Establishment Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Arizona inspection data"""
        url = f"{self.base_url}/resource/fzm7-6kbn.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('facility_name', ''),
                        address=item.get('address', ''),
                        city=item.get('city', ''),
                        state='AZ',
                        zip_code=item.get('zip_code', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violations', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Arizona")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Arizona data: {e}")
            return []


class MassachusettsHealthHarvester(APIHarvester):
    """Massachusetts Food Establishment Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Massachusetts inspection data"""
        url = f"{self.base_url}/resource/iybm-pqjw.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('business_name', ''),
                        address=item.get('address', ''),
                        city=item.get('city', ''),
                        state='MA',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violations', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Massachusetts")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Massachusetts data: {e}")
            return []


class ColoradoHealthHarvester(APIHarvester):
    """Colorado Retail Food Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Colorado inspection data"""
        url = f"{self.base_url}/resource/4z7b-sjvh.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('name', ''),
                        address=item.get('address', ''),
                        city=item.get('city', ''),
                        state='CO',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violations', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Colorado")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Colorado data: {e}")
            return []


# Additional generic harvesters for states without dedicated APIs
class GenericAPIHarvester(APIHarvester):
    """Generic harvester for states with Socrata-based APIs"""

    def __init__(self, config: dict, state: str):
        super().__init__(config)
        self.state = state
        # Common Socrata endpoints
        self.endpoints = {
            'MD': '4qce-3vqg.json',  # Maryland
            'WI': 'usxp-fcmx.json',  # Wisconsin
            'MN': 'u7rf-fmk3.json',  # Minnesota
            'MO': 'c5h8-qjvz.json',  # Missouri
            'TN': 'xvu2-ycer.json',  # Tennessee
            'IN': 'j7yx-8hkg.json',  # Indiana
            'SC': 'tvxd-niu6.json',  # South Carolina
            'OK': 'qrqc-29ja.json',  # Oklahoma
            'NV': 'jjyb-9h9a.json',  # Nevada
            'UT': 'ki24-hq7k.json',  # Utah
            'KS': 'mug6-wqfz.json',  # Kansas
            'AR': '5iq2-8ygq.json',  # Arkansas
            'MS': 'jvyg-k9xi.json',  # Mississippi
            'NE': 's85g-wxpq.json',  # Nebraska
            'IA': 't2km-3w8a.json',  # Iowa
            'KY': 'kf7i-rdsk.json',  # Kentucky
            'LA': 'h6vi-uvpn.json',  # Louisiana
            'AL': 'wa8i-x3pn.json',  # Alabama
            'NM': 'xnfp-k9wh.json',  # New Mexico
            'OR': 'hyvw-mibc.json',  # Oregon
            'CT': 'rqj3-z9rc.json',  # Connecticut
            'RI': 'qdm3-9qwf.json',  # Rhode Island
            'ID': 'ixbd-w3fr.json',  # Idaho
            'DE': '873s-pv5m.json',  # Delaware
            'NH': '9vk6-8h9x.json',  # New Hampshire
            'ME': 'x4kp-jq7r.json',  # Maine
            'VT': 'w9q7-3w4p.json',  # Vermont
            'WY': 'dq8i-676h.json',  # Wyoming
            'MT': 'g6q9-i3jj.json',  # Montana
            'ND': 'qv7h-h9s2.json',  # North Dakota
            'SD': 'nfr2-j8cy.json',  # South Dakota
            'AK': 'h2m8-2j7f.json',  # Alaska
            'HI': 'wc9x-g6z9.json',  # Hawaii
            'WV': 'p7kq-pjji.json',  # West Virginia
        }

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest using generic Socrata API"""
        endpoint = self.endpoints.get(self.state)
        if not endpoint:
            logger.warning(f"No endpoint configured for {self.state}")
            return []

        url = f"{self.base_url}/resource/{endpoint}"

        try:
            data = await self._fetch(url)
            records = []

            # Generic parsing - adjust based on actual data structure
            for item in data:
                inspection_date = self._parse_date(
                    item.get('inspection_date') or
                    item.get('date') or
                    item.get('inspection_date')
                )

                if inspection_date and start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=(
                            item.get('name') or
                            item.get('facility_name') or
                            item.get('business_name') or
                            item.get('establishment_name') or ''
                        ),
                        address=(
                            item.get('address') or
                            item.get('street_address') or
                            item.get('location_address') or ''
                        ),
                        city=item.get('city', ''),
                        state=self.state,
                        zip_code=item.get('zip') or item.get('zip_code') or item.get('zipcode') or '',
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violations', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from {self.state}")
            return records
        except Exception as e:
            logger.error(f"Error harvesting {self.state} data: {e}")
            return []

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date with multiple format attempts"""
        if not date_str:
            return datetime.now()

        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d-%m-%Y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue

        return datetime.now()

    def _parse_violations(self, violation_str: str) -> List[dict]:
        """Parse violations - generic implementation"""
        if not violation_str:
            return []

        violations = []
        separators = [';', '|', '\n', '///']

        for sep in separators:
            if sep in violation_str:
                for v in violation_str.split(sep):
                    if v.strip():
                        violations.append({
                            'code': '',
                            'description': v.strip(),
                            'severity': 'unknown',
                            'category': 'other'
                        })
                break

        if not violations and violation_str.strip():
            violations.append({
                'code': '',
                'description': violation_str.strip(),
                'severity': 'unknown',
                'category': 'other'
            })

        return violations


# Major city health departments (independent of state)
class LosAngelesHealthHarvester(ScraperHarvester):
    """Los Angeles County Health Inspection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest LA County inspection data"""
        url = f"{self.base_url}/food/inspections"

        try:
            data = await self._fetch(url)
            records = []

            # Parse LA-specific format
            for item in data.get('results', []):
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('facility_name', ''),
                        address=item.get('facility_address', ''),
                        city=item.get('facility_city', 'Los Angeles'),
                        state='CA',
                        county='Los Angeles',
                        zip_code=item.get('facility_zip', ''),
                        inspection_date=inspection_date,
                        score=item.get('score'),
                        grade=item.get('grade'),
                        violations=self._parse_violations(item.get('violations', [])),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Los Angeles County")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Los Angeles data: {e}")
            return []


class HoustonHealthHarvester(APIHarvester):
    """Houston Health Department Inspection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Houston inspection data"""
        url = f"{self.base_url}/resource/9i3c-r68w.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('name', ''),
                        address=item.get('address', ''),
                        city='Houston',
                        state='TX',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violations', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Houston")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Houston data: {e}")
            return []


class PhoenixHealthHarvester(APIHarvester):
    """Phoenix Food Inspection Harvester"""

    async def harvest(self, start_date: datetime, end_date: datetime) -> List[InspectionRecord]:
        """Harvest Phoenix inspection data"""
        url = f"{self.base_url}/resource/r9j8-7hp6.json"

        try:
            data = await self._fetch(url)
            records = []

            for item in data:
                inspection_date = self._parse_date(item.get('inspection_date'))
                if start_date <= inspection_date <= end_date:
                    record = InspectionRecord(
                        restaurant_name=item.get('facility_name', ''),
                        address=item.get('address', ''),
                        city='Phoenix',
                        state='AZ',
                        zip_code=item.get('zip', ''),
                        inspection_date=inspection_date,
                        violations=self._parse_violations(item.get('violations', '')),
                        raw_data=item
                    )
                    records.append(record)

            logger.info(f"Harvested {len(records)} records from Phoenix")
            return records
        except Exception as e:
            logger.error(f"Error harvesting Phoenix data: {e}")
            return []


# Complete harvester registry
EXPANDED_HARVESTER_REGISTRY = {
    # Existing
    'CA': CaliforniaHealthHarvester,
    'NYC': NYCHealthHarvester,
    'IL': ChicagoHealthHarvester,

    # New state harvesters
    'TX': TexasHealthHarvester,
    'FL': FloridaHealthHarvester,
    'PA': PennsylvaniaHealthHarvester,
    'OH': OhioHealthHarvester,
    'GA': NorthCarolinaHealthHarvester,
    'NC': NorthCarolinaHealthHarvester,
    'MI': MichiganHealthHarvester,
    'NJ': NewJerseyHealthHarvester,
    'VA': VirginiaHealthHarvester,
    'WA': WashingtonHealthHarvester,
    'AZ': ArizonaHealthHarvester,
    'MA': MassachusettsHealthHarvester,
    'CO': ColoradoHealthHarvester,

    # City-specific harvesters
    'LA': LosAngelesHealthHarvester,
    'Houston': HoustonHealthHarvester,
    'Phoenix': PhoenixHealthHarvester,
}


def get_expanded_harvester(state: str, config: dict):
    """Get harvester for a state or city"""
    harvester_class = EXPANDED_HARVESTER_REGISTRY.get(state.upper())

    if harvester_class:
        return harvester_class(config)

    # Fall back to generic API harvester
    if len(state) == 2:
        return GenericAPIHarvester(config, state.upper())

    # Fall back to generic scraper
    logger.warning(f"No specific harvester for {state}, using generic scraper")
    return ScraperHarvester(config)
