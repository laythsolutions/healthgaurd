"""Local storage for offline operation"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalStorage:
    """SQLite-based local storage (works offline)"""

    def __init__(self, db_path='/data/local_data.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.init_db()
        logger.info(f"LocalStorage initialized at {self.db_path}")

    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Sensor readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                data TEXT NOT NULL,
                synced INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                device_id TEXT,
                location TEXT,
                temperature REAL,
                threshold_min REAL,
                threshold_max REAL,
                message TEXT NOT NULL,
                synced INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Device configs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_configs (
                device_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT,
                temp_min_f REAL,
                temp_max_f REAL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_readings_device ON sensor_readings(device_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_device ON alerts(device_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_synced ON alerts(synced)')

        conn.commit()
        conn.close()

    def store_sensor_reading(self, message):
        """Store sensor reading locally"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO sensor_readings (device_id, timestamp, data, synced)
                VALUES (?, ?, ?, ?)
            ''', (
                message['device_id'],
                message['timestamp'],
                json.dumps(message['data']),
                0  # Not synced yet
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to store sensor reading: {e}")

    def store_alert(self, alert):
        """Store alert locally"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO alerts (alert_type, severity, device_id, location, temperature,
                                  threshold_min, threshold_max, message, synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert['alert_type'],
                alert['severity'],
                alert.get('device_id'),
                alert.get('location'),
                alert.get('temperature'),
                alert.get('threshold_min'),
                alert.get('threshold_max'),
                alert['message'],
                0  # Not synced yet
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to store alert: {e}")

    def get_recent_readings(self, device_id, hours=24):
        """Get recent readings for a device"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

            cursor.execute('''
                SELECT device_id, timestamp, data FROM sensor_readings
                WHERE device_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (device_id, since))

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'device_id': row[0],
                    'timestamp': row[1],
                    'data': json.loads(row[2])
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Failed to get recent readings: {e}")
            return []

    def load_device_configs(self):
        """Load all device configurations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT device_id, name, location, temp_min_f, temp_max_f FROM device_configs')
            rows = cursor.fetchall()
            conn.close()

            configs = {}
            for row in rows:
                configs[row[0]] = {
                    'name': row[1],
                    'location': row[2],
                    'temp_min_f': row[3],
                    'temp_max_f': row[4]
                }

            return configs

        except Exception as e:
            logger.error(f"Failed to load device configs: {e}")
            return {}

    def save_device_configs(self, configs):
        """Save device configurations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for device_id, config in configs.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO device_configs (device_id, name, location, temp_min_f, temp_max_f)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    device_id,
                    config.get('name', device_id),
                    config.get('location'),
                    config.get('temp_min_f'),
                    config.get('temp_max_f')
                ))

            conn.commit()
            conn.close()

            logger.info(f"Saved {len(configs)} device configurations")

        except Exception as e:
            logger.error(f"Failed to save device configs: {e}")

    def get_unsynced_readings(self, limit=1000):
        """Get unsynced sensor readings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, device_id, timestamp, data FROM sensor_readings
                WHERE synced = 0
                LIMIT ?
            ''', (limit,))

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'id': row[0],
                    'device_id': row[1],
                    'timestamp': row[2],
                    'data': json.loads(row[3])
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Failed to get unsynced readings: {e}")
            return []

    def mark_as_synced(self, table, ids):
        """Mark records as synced"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(ids))
            cursor.execute(f'UPDATE {table} SET synced = 1 WHERE id IN ({placeholders})', ids)

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to mark as synced: {e}")
