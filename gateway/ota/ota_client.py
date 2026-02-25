#!/usr/bin/env python3
"""
OTA Update Client - Runs on Edge Gateway
Handles update download, verification, installation, and rollback
"""

import os
import sys
import json
import hashlib
import shutil
import subprocess
import logging
import requests
import tempfile
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger(__name__)


class OTAUpdateClient:
    """OTA update client for edge gateway"""

    def __init__(self, config: Dict):
        self.config = config
        self.base_dir = Path('/opt/restaurant-gateway')
        self.backups_dir = self.base_dir / 'backups'
        self.temp_dir = Path(tempfile.mkdtemp(prefix='ota_'))
        os.chmod(self.temp_dir, 0o700)
        self.public_key_path = config['public_key_path']
        self.gateway_id = config['gateway_id']
        self.api_url = config['api_url']

        # Create directories
        self.backups_dir.mkdir(parents=True, exist_ok=True)

        self.current_version = self._get_current_version()
        logger.info(f"OTA Client initialized - Current version: {self.current_version}")

    def check_for_updates(self) -> Optional[Dict]:
        """Check if update is available"""

        logger.info("Checking for updates...")

        try:
            response = requests.get(
                f"{self.api_url}/ota/updates/check",
                params={
                    'gateway_id': self.gateway_id,
                    'current_version': self.current_version
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if data.get('update_available'):
                    logger.info(f"Update available: {data['version']}")
                    return {
                        'version': data['version'],
                        'description': data['description'],
                        'critical': data.get('critical', False),
                        'manifest_url': data['manifest_url'],
                        'signature_url': data['signature_url']
                    }

            logger.info("No updates available")
            return None

        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return None

    def download_update(self, manifest_url: str, signature_url: str) -> tuple:
        """Download update manifest and signature"""

        logger.info("Downloading update...")

        try:
            # Download manifest
            manifest_response = requests.get(manifest_url, timeout=30)
            manifest_response.raise_for_status()
            manifest_json = manifest_response.text

            # Download signature
            sig_response = requests.get(signature_url, timeout=30)
            sig_response.raise_for_status()
            signature = sig_response.text

            logger.info("Update downloaded successfully")
            return manifest_json, signature

        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            raise

    def verify_update(self, manifest_json: str, signature: str) -> bool:
        """Verify update signature"""

        logger.info("Verifying update signature...")

        try:
            # Load public key
            with open(self.public_key_path, 'rb') as key_file:
                public_key = load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )

            # Verify signature
            manifest_bytes = manifest_json.encode('utf-8')
            signature_bytes = bytes.fromhex(signature)

            try:
                public_key.verify(
                    signature_bytes,
                    manifest_bytes,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )

                logger.info("✅ Signature verified")
                return True

            except InvalidSignature:
                logger.error("❌ Invalid signature!")
                return False

        except Exception as e:
            logger.error(f"Failed to verify signature: {e}")
            return False

    def apply_update(self, manifest_json: str) -> bool:
        """Apply update with automatic rollback on failure"""

        manifest = json.loads(manifest_json)
        backup_path = None

        try:
            logger.info(f"Applying update {manifest['version']}...")

            # 1. Create backup
            logger.info("Creating system backup...")
            backup_path = self._create_system_backup()

            # 2. Download new Docker images
            logger.info("Pulling new Docker images...")
            self._pull_docker_images(manifest['docker_images'])

            # 3. Stop services
            logger.info("Stopping services...")
            subprocess.run(['docker-compose', 'down'], check=True, cwd=self.base_dir)

            # 4. Update docker-compose.yml if needed
            if manifest.get('config_changes'):
                logger.info("Updating configuration...")
                self._update_configuration(manifest['config_changes'])

            # 5. Run migrations if any
            if manifest.get('migrations'):
                logger.info("Running migrations...")
                self._run_migrations(manifest['migrations'])

            # 6. Start services
            logger.info("Starting services...")
            subprocess.run(['docker-compose', 'up', '-d'], check=True, cwd=self.base_dir)

            # 7. Wait for services to start
            logger.info("Waiting for services to start...")
            time.sleep(30)

            # 8. Health check
            if not self._verify_system_health():
                raise Exception("Health check failed")

            # 9. Update version
            self._update_version(manifest['version'])

            # 10. Report success
            self._report_update_success(manifest['version'])

            logger.info(f"✅ Update {manifest['version']} applied successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Update failed: {e}")

            # Automatic rollback
            if backup_path:
                logger.info("Rolling back...")
                self._restore_from_backup(backup_path)

            # Report failure
            self._report_update_failure(manifest['version'], str(e))

            return False

    def _create_system_backup(self) -> Path:
        """Create backup of current system state"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backups_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True)

        # Backup docker-compose.yml
        shutil.copy(self.base_dir / 'docker-compose.yml', backup_path / 'docker-compose.yml')

        # Backup .env file
        if (self.base_dir / '.env').exists():
            shutil.copy(self.base_dir / '.env', backup_path / '.env')

        # Backup config directory
        config_dir = self.base_dir / 'config'
        if config_dir.exists():
            shutil.copytree(config_dir, backup_path / 'config')

        # Backup local database
        self._backup_database(backup_path)

        # Create metadata
        metadata = {
            'version': self.current_version,
            'timestamp': timestamp,
            'backup_path': str(backup_path)
        }

        (backup_path / 'metadata.json').write_text(json.dumps(metadata, indent=2))

        logger.info(f"Backup created at {backup_path}")
        return backup_path

    def _backup_database(self, backup_path: Path):
        """Backup PostgreSQL database"""

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_path / f"database_{timestamp}.sql"

            # Run pg_dump from within the Docker container
            subprocess.run([
                'docker', 'exec', 'local-db',
                'pg_dump', '-U', 'local_user', 'restaurant_local',
                '-f', f'/backups/backup_{timestamp}.sql'
            ], check=True)

            logger.info("Database backup created")

        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            # Don't fail the backup process

    def _pull_docker_images(self, images: Dict[str, str]):
        """Pull new Docker images"""

        for service, image_tag in images.items():
            logger.info(f"Pulling {service}: {image_tag}")
            subprocess.run(['docker', 'pull', image_tag], check=True)

            # Update docker-compose.yml to use new image
            # This is a simplified version - you'd want proper YAML editing
            compose_file = self.base_dir / 'docker-compose.yml'
            content = compose_file.read_text()
            content = content.replace(f'{service}:', f'{service}_old:')  # Mark old

    def _update_configuration(self, config_changes: List[Dict]):
        """Update configuration files"""

        for change in config_changes:
            file_path = self.base_dir / change['file']
            action = change['action']

            if action == 'replace':
                file_path.write_text(change['content'])
            elif action == 'append':
                with open(file_path, 'a') as f:
                    f.write(change['content'])
            elif action == 'json_merge':
                import json
                existing = json.loads(file_path.read_text())
                merged = {**existing, **change['content']}
                file_path.write_text(json.dumps(merged, indent=2))

    def _run_migrations(self, migrations: list):
        """Run database migrations"""

        # Allowlist of safe migration commands
        allowed_prefixes = ['docker', 'python', 'alembic']

        for migration in migrations:
            args = migration.split()
            if not args or args[0] not in allowed_prefixes:
                logger.warning(f"Skipping disallowed migration command: {migration}")
                continue
            logger.info(f"Running migration: {migration}")
            subprocess.run(args, check=True)

    def _verify_system_health(self) -> bool:
        """Verify system health after update"""

        required_services = [
            'zigbee2mqtt',
            'mosquitto',
            'mqtt-bridge',
            'local-db'
        ]

        for service in required_services:
            try:
                result = subprocess.run([
                    'docker', 'inspect', '-f',
                    '{{.State.Running}}', service
                ], capture_output=True, text=True, check=True)

                if result.stdout.strip() != 'true':
                    logger.error(f"Service {service} is not running")
                    return False

            except subprocess.CalledProcessError:
                logger.error(f"Failed to check service {service}")
                return False

        # Check MQTT connectivity
        if not self._test_mqtt_connection():
            logger.error("MQTT connection test failed")
            return False

        logger.info("✅ All health checks passed")
        return True

    def _test_mqtt_connection(self) -> bool:
        """Test MQTT broker connection"""

        try:
            import paho.mqtt.client as mqtt

            client = mqtt.Client()
            client.connect('localhost', 1883, timeout=5)
            client.disconnect()
            return True

        except Exception as e:
            logger.error(f"MQTT test failed: {e}")
            return False

    def _restore_from_backup(self, backup_path: Path):
        """Restore system from backup"""

        logger.info(f"Restoring from {backup_path}...")

        try:
            # Stop services
            subprocess.run(['docker-compose', 'down'], check=False, cwd=self.base_dir)

            # Restore docker-compose.yml
            shutil.copy(backup_path / 'docker-compose.yml', self.base_dir / 'docker-compose.yml')

            # Restore .env
            if (backup_path / '.env').exists():
                shutil.copy(backup_path / '.env', self.base_dir / '.env')

            # Restore config
            if (backup_path / 'config').exists():
                config_dir = self.base_dir / 'config'
                if config_dir.exists():
                    shutil.rmtree(config_dir)
                shutil.copytree(backup_path / 'config', config_dir)

            # Restore database
            self._restore_database(backup_path)

            # Start services
            subprocess.run(['docker-compose', 'up', '-d'], check=True, cwd=self.base_dir)

            # Wait for services
            time.sleep(30)

            logger.info("✅ Rollback complete")

        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            # Critical situation - manual intervention required
            self._report_critical_failure(str(e))

    def _restore_database(self, backup_path: Path):
        """Restore database from backup"""

        # Find latest backup file
        backup_files = list(backup_path.glob('database_*.sql'))

        if backup_files:
            backup_file = backup_files[0]

            # Restore from within Docker container
            subprocess.run([
                'docker', 'exec', 'local-db',
                'psql', '-U', 'local_user', '-d', 'restaurant_local',
                '-f', f'/backups/{backup_file.name}'
            ], check=True)

            logger.info("Database restored")

    def _update_version(self, version: str):
        """Update current version"""

        version_file = self.base_dir / 'VERSION'
        version_file.write_text(version)
        self.current_version = version

    def _get_current_version(self) -> str:
        """Get current version"""

        version_file = self.base_dir / 'VERSION'

        if version_file.exists():
            return version_file.read_text().strip()

        # Fallback: read from git tag
        try:
            result = subprocess.run(
                ['git', 'describe', '--tags', '--always'],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            return result.stdout.strip()
        except:
            return '1.0.0'  # Default version

    def _report_update_success(self, version: str):
        """Report successful update to cloud"""

        try:
            requests.post(
                f"{self.api_url}/ota/updates/success",
                json={
                    'gateway_id': self.gateway_id,
                    'version': version,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=10
            )
        except Exception as e:
            logger.error(f"Failed to report success: {e}")

    def _report_update_failure(self, version: str, error: str):
        """Report update failure to cloud"""

        try:
            requests.post(
                f"{self.api_url}/ota/updates/failure",
                json={
                    'gateway_id': self.gateway_id,
                    'version': version,
                    'error': error,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=10
            )
        except Exception as e:
            logger.error(f"Failed to report failure: {e}")

    def _report_critical_failure(self, error: str):
        """Report critical failure requiring manual intervention"""

        logger.critical(f"CRITICAL FAILURE: {error}")
        # Send alert via all channels
        # This would trigger SMS, email, etc.


def main():
    """CLI for OTA client"""

    import argparse

    parser = argparse.ArgumentParser(description='OTA Update Client')
    parser.add_argument('command', choices=['check', 'update', 'rollback'], help='Command')
    parser.add_argument('--version', help='Specific version to update to')
    parser.add_argument('--force', action='store_true', help='Force update')

    args = parser.parse_args()

    config = {
        'gateway_id': os.getenv('GATEWAY_ID', 'local_gateway'),
        'api_url': os.getenv('API_URL', 'https://api.healthguard.com'),
        'public_key_path': '/opt/restaurant-gateway/keys/ota_public.key'
    }

    client = OTAUpdateClient(config)

    if args.command == 'check':
        update = client.check_for_updates()

        if update:
            print(f"✅ Update Available: {update['version']}")
            print(f"   {update['description']}")
            if update['critical']:
                print("   ⚠️  CRITICAL UPDATE")
        else:
            print("✅ No updates available")

    elif args.command == 'update':
        if args.version:
            # Update to specific version
            print(f"Updating to version {args.version}...")
            # Implementation would download specific version
        else:
            # Check and apply latest
            update_info = client.check_for_updates()

            if update_info:
                manifest, signature = client.download_update(
                    update_info['manifest_url'],
                    update_info['signature_url']
                )

                if client.verify_update(manifest, signature):
                    client.apply_update(manifest)
                else:
                    print("❌ Signature verification failed")
                    sys.exit(1)
            else:
                print("No updates available")

    elif args.command == 'rollback':
        # Rollback to last backup
        backups_dir = Path('/opt/restaurant-gateway/backups')
        backups = sorted(backups_dir.glob('backup_*'), reverse=True)

        if backups:
            latest_backup = backups[0]
            print(f"Rolling back to {latest_backup}...")
            client._restore_from_backup(latest_backup)
            print("✅ Rollback complete")
        else:
            print("No backups found")


if __name__ == '__main__':
    main()
