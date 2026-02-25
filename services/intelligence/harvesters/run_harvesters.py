"""Main harvester runner"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path

from state_harvesters import get_harvester, InspectionRecord

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Configuration for each state's API
STATE_CONFIGS = {
    'CA': {
        'base_url': 'https://data.californiagovernment.org/resource',
        'api_key': None,
        'rate_limit': 1000,
    },
    'NYC': {
        'base_url': 'https://data.cityofnewyork.us',
        'api_key': None,
        'rate_limit': 1000,
    },
    'IL': {
        'base_url': 'https://data.cityofchicago.org',
        'api_key': None,
        'rate_limit': 1000,
    },
    # Add more state configs here
}


async def harvest_state(
    state: str,
    start_date: datetime,
    end_date: datetime,
    config: Dict = None
) -> List[InspectionRecord]:
    """Harvest data for a single state"""
    if config is None:
        config = STATE_CONFIGS.get(state, {})

    logger.info(f"Harvesting data for {state} from {start_date} to {end_date}")

    try:
        harvester = get_harvester(state, config)
        records = await harvester.harvest(start_date, end_date)

        logger.info(f"Harvested {len(records)} records for {state}")
        return records

    except Exception as e:
        logger.error(f"Failed to harvest {state}: {e}", exc_info=True)
        return []


async def harvest_all_states(
    states: List[str] = None,
    days_back: int = 30
) -> Dict[str, List[InspectionRecord]]:
    """Harvest data for multiple states"""
    if states is None:
        states = list(STATE_CONFIGS.keys())

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    logger.info(f"Starting harvest for {len(states)} states")

    # Harvest all states concurrently
    tasks = [
        harvest_state(state, start_date, end_date)
        for state in states
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Combine results
    all_records = {}
    for state, records in zip(states, results):
        if isinstance(records, Exception):
            logger.error(f"Error harvesting {state}: {records}")
            all_records[state] = []
        else:
            all_records[state] = records

    # Log summary
    total_records = sum(len(records) for records in all_records.values())
    logger.info(f"Harvest complete! Total records: {total_records}")

    return all_records


async def search_restaurants(
    name: str,
    state: str = None,
    city: str = None
) -> List[InspectionRecord]:
    """Search for restaurants across all available states"""
    states = [state] if state else list(STATE_CONFIGS.keys())

    all_results = []

    for st in states:
        try:
            config = STATE_CONFIGS.get(st, {})
            harvester = get_harvester(st, config)
            results = await harvester.search_by_name(name, city)
            all_results.extend(results)

            logger.info(f"Found {len(results)} results in {st}")

        except Exception as e:
            logger.error(f"Error searching {st}: {e}")

    logger.info(f"Total search results: {len(all_results)}")
    return all_results


def save_records(records: List[InspectionRecord], filename: str):
    """Save records to file"""
    import json

    output = []
    for record in records:
        output.append({
            'restaurant_name': record.restaurant_name,
            'address': record.address,
            'city': record.city,
            'state': record.state,
            'zip_code': record.zip_code,
            'inspection_date': record.inspection_date.isoformat(),
            'score': record.score,
            'violations': record.violations,
            'risk_level': record.risk_level,
            'raw_data': record.raw_data,
        })

    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

    logger.info(f"Saved {len(output)} records to {filename}")


async def main():
    """Main entry point"""
    import sys

    command = sys.argv[1] if len(sys.argv) > 1 else 'harvest'

    if command == 'harvest':
        # Harvest recent data
        days_back = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        records = await harvest_all_states(days_back=days_back)

        # Save each state's records
        for state, state_records in records.items():
            if state_records:
                filename = f"data/inspections_{state}_{datetime.now().strftime('%Y%m%d')}.json"
                save_records(state_records, filename)

    elif command == 'search':
        name = sys.argv[2] if len(sys.argv) > 2 else ''
        state = sys.argv[3] if len(sys.argv) > 3 else None

        if not name:
            logger.error("Please provide a restaurant name to search")
            return

        records = await search_restaurants(name, state)

        filename = f"data/search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_records(records, filename)

    else:
        logger.error(f"Unknown command: {command}")
        logger.info("Available commands: harvest, search")


if __name__ == '__main__':
    asyncio.run(main())
