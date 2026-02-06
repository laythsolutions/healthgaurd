"""Utility functions"""

import logging
import sys


def setup_logging():
    """Setup structured logging"""

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/data/mqtt_bridge.log')
        ]
    )

    return logging.getLogger('mqtt_bridge')
