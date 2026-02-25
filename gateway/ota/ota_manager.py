#!/usr/bin/env python3
"""
OTA Update Manager - Runs on Cloud
Manages update manifests, versions, and rollouts
"""

import os
import json
import hashlib
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import boto3
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger(__name__)


@dataclass
class UpdateManifest:
    """Update manifest"""
    version: str
    release_date: str
    description: str
    docker_images: Dict[str, str]  # service: image_tag
    config_changes: List[Dict]
    migrations: List[str]
    pre_update_hooks: List[str]
    post_update_hooks: List[str]
    rollback_commands: List[str]
    min_gateway_version: str
    max_gateway_version: str
    critical: bool = False
    rollback_safe: bool = True

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'UpdateManifest':
        data = json.loads(json_str)
        return cls(**data)


class OTAUpdateManager:
    """Manage OTA updates from cloud"""

    def __init__(self, config: Dict):
        self.config = config
        self.s3_client = boto3.client('s3')
        self.bucket_name = config['s3_bucket']
        self.private_key_path = config['private_key_path']
        self.manifests_dir = Path(config['manifests_dir'])
        self.manifests_dir.mkdir(parents=True, exist_ok=True)

    def create_update(
        self,
        version: str,
        description: str,
        docker_images: Dict[str, str],
        config_changes: List[Dict] = None,
        migrations: List[str] = None,
        critical: bool = False
    ) -> UpdateManifest:
        """Create a new update manifest"""

        logger.info(f"Creating update {version}")

        manifest = UpdateManifest(
            version=version,
            release_date=datetime.now().isoformat(),
            description=description,
            docker_images=docker_images,
            config_changes=config_changes or [],
            migrations=migrations or [],
            pre_update_hooks=[],
            post_update_hooks=[],
            rollback_commands=[
                "docker-compose down",
                f"git checkout HEAD~1",  # Rollback git
                "docker-compose up -d"
            ],
            min_gateway_version="1.0.0",
            max_gateway_version="2.0.0",
            critical=critical,
            rollback_safe=True
        )

        # Save manifest locally
        manifest_path = self.manifests_dir / f"update_{version}.json"
        manifest_path.write_text(manifest.to_json())

        # Sign manifest
        signature = self._sign_manifest(manifest)
        signature_path = self.manifests_dir / f"update_{version}.sig"
        signature_path.write_text(signature)

        # Upload to S3
        self._upload_to_s3(manifest, signature)

        logger.info(f"Update {version} created and uploaded")
        return manifest

    def _sign_manifest(self, manifest: UpdateManifest) -> str:
        """Sign manifest with private key"""

        with open(self.private_key_path, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

        manifest_json = manifest.to_json().encode()
        signature = private_key.sign(
            manifest_json,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature.hex()

    def _upload_to_s3(self, manifest: UpdateManifest, signature: str):
        """Upload manifest and signature to S3"""

        # Upload manifest
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=f"updates/{manifest.version}/manifest.json",
            Body=manifest.to_json()
        )

        # Upload signature
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=f"updates/{manifest.version}/manifest.sig",
            Body=signature
        )

        logger.info(f"Uploaded update {manifest.version} to S3")

    def get_latest_version(self, gateway_version: str) -> Optional[UpdateManifest]:
        """Get latest available update for a gateway version"""

        # List all updates in S3
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix='updates/'
        )

        if 'Contents' not in response:
            return None

        # Get all manifests
        updates = []
        for obj in response['Contents']:
            key = obj['Key']
            if 'manifest.json' in key:
                version = key.split('/')[1]
                manifest = self.get_manifest(version)
                if manifest:
                    updates.append(manifest)

        # Filter compatible versions
        compatible = [
            u for u in updates
            if self._is_version_compatible(gateway_version, u.min_gateway_version, u.max_gateway_version)
        ]

        if not compatible:
            return None

        # Return latest
        return max(compatible, key=lambda x: x.version)

    def get_manifest(self, version: str) -> Optional[UpdateManifest]:
        """Download manifest from S3"""

        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=f"updates/{version}/manifest.json"
            )

            manifest_json = response['Body'].read().decode()
            return UpdateManifest.from_json(manifest_json)

        except Exception as e:
            logger.error(f"Failed to get manifest {version}: {e}")
            return None

    def _is_version_compatible(
        self,
        gateway_version: str,
        min_version: str,
        max_version: str
    ) -> bool:
        """Check if versions are compatible"""

        from packaging import version

        try:
            gateway = version.parse(gateway_version)
            minimum = version.parse(min_version)
            maximum = version.parse(max_version)

            return minimum <= gateway <= maximum
        except:
            return True  # Assume compatible if parsing fails

    def rollout_update(
        self,
        version: str,
        gateway_ids: List[str],
        percentage: int = 100,
        stagger_minutes: int = 5
    ):
        """Roll out update to gateways"""

        manifest = self.get_manifest(version)
        if not manifest:
            raise ValueError(f"Update {version} not found")

        logger.info(f"Rolling out {version} to {len(gateway_ids)} gateways")

        # Calculate batch size
        batch_size = max(1, int(len(gateway_ids) * (percentage / 100)))

        # Split into batches
        batches = [
            gateway_ids[i:i + batch_size]
            for i in range(0, len(gateway_ids), batch_size)
        ]

        for i, batch in enumerate(batches):
            logger.info(f"Deploying batch {i+1}/{len(batches)} ({len(batch)} gateways)")

            for gateway_id in batch:
                # Trigger update via MQTT
                self._trigger_gateway_update(gateway_id, manifest)

            # Wait before next batch
            if i < len(batches) - 1:
                logger.info(f"Waiting {stagger_minutes} minutes before next batch")
                import time
                time.sleep(stagger_minutes * 60)

    def _trigger_gateway_update(self, gateway_id: str, manifest: UpdateManifest):
        """Trigger update on gateway via MQTT"""

        # Publish update command to gateway
        # Implementation depends on your MQTT setup
        import paho.mqtt.client as mqtt

        client = mqtt.Client()
        client.connect(self.config['mqtt_broker'], 1883, 60)

        update_command = {
            'command': 'update',
            'version': manifest.version,
            'manifest_url': f"https://{self.bucket_name}.s3.amazonaws.com/updates/{manifest.version}/manifest.json",
            'signature_url': f"https://{self.bucket_name}.s3.amazonaws.com/updates/{manifest.version}/manifest.sig",
            'critical': manifest.critical
        }

        client.publish(f"gateway/{gateway_id}/commands/update", json.dumps(update_command))
        client.disconnect()

        logger.info(f"Triggered update on gateway {gateway_id}")

    def get_rollout_status(self, version: str) -> Dict:
        """Get rollout status for an update"""

        # Query database for update status across all gateways
        # This would query your update tracking table
        return {
            'version': version,
            'total_gateways': 100,
            'updated': 65,
            'failed': 2,
            'pending': 33,
            'rollout_percentage': 65
        }


def main():
    """CLI for OTA manager"""

    import argparse

    parser = argparse.ArgumentParser(description='OTA Update Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create update command
    create_parser = subparsers.add_parser('create-update', help='Create new update')
    create_parser.add_argument('--version', required=True, help='Version number (e.g., 1.2.0)')
    create_parser.add_argument('--description', required=True, help='Update description')
    create_parser.add_argument('--images', required=True, help='Docker images (JSON)')
    create_parser.add_argument('--critical', action='store_true', help='Critical update')

    # Rollout command
    rollout_parser = subparsers.add_parser('rollout', help='Roll out update')
    rollout_parser.add_argument('--version', required=True, help='Version to rollout')
    rollout_parser.add_argument('--gateways', required=True, help='Gateway IDs (comma-separated)')
    rollout_parser.add_argument('--percentage', type=int, default=100, help='Percentage to rollout')
    rollout_parser.add_argument('--stagger', type=int, default=5, help='Minutes between batches')

    args = parser.parse_args()

    config = {
        's3_bucket': 'healthguard-updates',
        'private_key_path': '/keys/ota_private.key',
        'manifests_dir': '/var/lib/ota/manifests',
        'mqtt_broker': 'mqtt.healthguard.com'
    }

    manager = OTAUpdateManager(config)

    if args.command == 'create-update':
        docker_images = json.loads(args.images)

        manifest = manager.create_update(
            version=args.version,
            description=args.description,
            docker_images=docker_images,
            critical=args.critical
        )

        print(f"✅ Update {args.version} created successfully")

    elif args.command == 'rollout':
        gateway_ids = args.gateways.split(',')

        manager.rollout_update(
            version=args.version,
            gateway_ids=gateway_ids,
            percentage=args.percentage,
            stagger_minutes=args.stagger
        )

        print(f"✅ Rolling out {args.version} to {len(gateway_ids)} gateways")


if __name__ == '__main__':
    main()
