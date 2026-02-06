"""Serializers for OTA models"""

from rest_framework import serializers
from .models import OTAManifest, GatewayUpdateStatus, GatewayBackup


class OTAManifestSerializer(serializers.ModelSerializer):
    """Serializer for OTA manifests"""

    class Meta:
        model = OTAManifest
        fields = [
            'id', 'version', 'release_date', 'description', 'docker_images',
            'config_changes', 'migrations', 'pre_update_hooks', 'post_update_hooks',
            'rollback_commands', 'min_gateway_version', 'max_gateway_version',
            'critical', 'rollback_safe', 'requires_reboot', 'manifest_url',
            'signature_url', 'status', 'rollout_percentage', 'auto_approve',
            'total_gateways', 'updated_gateways', 'failed_gateways',
            'success_rate', 'created_at'
        ]
        read_only_fields = [
            'release_date', 'total_gateways', 'updated_gateways',
            'failed_gateways', 'created_at'
        ]


class GatewayUpdateStatusSerializer(serializers.ModelSerializer):
    """Serializer for gateway update status"""

    manifest_version = serializers.CharField(source='manifest.version', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = GatewayUpdateStatus
        fields = [
            'id', 'gateway_id', 'restaurant', 'restaurant_name', 'manifest',
            'manifest_version', 'state', 'current_step', 'progress_percentage',
            'error_message', 'error_code', 'backup_created', 'backup_location',
            'started_at', 'completed_at', 'duration_seconds', 'retry_count',
            'max_retries', 'update_log'
        ]
        read_only_fields = ['started_at', 'completed_at', 'duration_seconds']


class GatewayBackupSerializer(serializers.ModelSerializer):
    """Serializer for gateway backups"""

    manifest_version = serializers.CharField(source='manifest.version', read_only=True)

    class Meta:
        model = GatewayBackup
        fields = [
            'id', 'gateway_id', 'manifest', 'manifest_version', 'backup_path',
            'version', 'size_bytes', 'includes_database', 'includes_config',
            'includes_docker_images', 'created_at', 'keep_until', 'is_cleaned_up'
        ]
        read_only_fields = ['created_at']


class UpdateCheckRequestSerializer(serializers.Serializer):
    """Serializer for update check request"""
    gateway_id = serializers.CharField()
    current_version = serializers.CharField()
