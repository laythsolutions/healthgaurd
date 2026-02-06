"""API views for OTA updates"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.conf import settings

from .models import OTAManifest, GatewayUpdateStatus, GatewayBackup
from .serializers import (
    OTAManifestSerializer,
    GatewayUpdateStatusSerializer,
    GatewayBackupSerializer
)
from .tasks import trigger_gateway_update, calculate_rollout_statistics


class OTAManifestViewSet(viewsets.ModelViewSet):
    """ViewSet for OTA manifests"""

    queryset = OTAManifest.objects.select_related('gateway_statuses').all()
    serializer_class = OTAManifestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        version_status = self.request.query_params.get('status')

        if version_status:
            queryset = queryset.filter(status=version_status)

        return queryset

    @action(detail=True, methods=['post'])
    def rollout(self, request, pk=None):
        """Initiate rollout to gateways"""
        manifest = self.get_object()

        gateway_ids = request.data.get('gateway_ids', [])
        percentage = request.data.get('percentage', 100)

        if not gateway_ids:
            return Response(
                {'error': 'gateway_ids required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate batch size
        batch_size = max(1, int(len(gateway_ids) * (percentage / 100)))

        # Create update status records
        created_count = 0
        for gateway_id in gateway_ids[:batch_size]:
            update_status, created = GatewayUpdateStatus.objects.get_or_create(
                gateway_id=gateway_id,
                manifest=manifest,
                defaults={'state': 'PENDING'}
            )

            if created:
                created_count += 1

                # Trigger update
                trigger_gateway_update.delay(update_status.id)

        manifest.status = 'ROLLING_OUT'
        manifest.rollout_percentage = percentage
        manifest.save()

        return Response({
            'message': f'Rollout initiated for {created_count} gateways',
            'manifest': OTAManifestSerializer(manifest).data
        })

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get rollout statistics"""
        manifest = self.get_object()

        stats = {
            'version': manifest.version,
            'status': manifest.status,
            'total_gateways': manifest.total_gateways,
            'updated_gateways': manifest.updated_gateways,
            'failed_gateways': manifest.failed_gateways,
            'success_rate': manifest.success_rate,
            'rollout_percentage': manifest.rollout_percentage,
        }

        return Response(stats)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark rollout as complete"""
        manifest = self.get_object()
        manifest.status = 'COMPLETED'
        manifest.save()

        return Response({'message': f'Manifest {manifest.version} marked as complete'})


class GatewayUpdateStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for gateway update status"""

    queryset = GatewayUpdateStatus.objects.select_related('manifest', 'restaurant').all()
    serializer_class = GatewayUpdateStatusSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        gateway_id = self.request.query_params.get('gateway_id')
        update_state = self.request.query_params.get('state')

        if gateway_id:
            queryset = queryset.filter(gateway_id=gateway_id)
        if update_state:
            queryset = queryset.filter(state=update_state)

        return queryset

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update progress from gateway"""
        update_status = self.get_object()

        # Update state and progress
        new_state = request.data.get('state')
        progress = request.data.get('progress_percentage')
        step = request.data.get('current_step')
        log = request.data.get('log')

        if new_state:
            update_status.state = new_state
        if progress is not None:
            update_status.progress_percentage = progress
        if step:
            update_status.current_step = step
        if log:
            update_status.log(log)

        update_status.save()

        return Response({'status': 'updated'})

    @action(detail=True, methods=['post'])
    def mark_success(self, request, pk=None):
        """Mark update as successful"""
        update_status = self.get_object()

        update_status.state = 'SUCCESS'
        update_status.completed_at = timezone.now()
        if update_status.started_at:
            duration = update_status.completed_at - update_status.started_at
            update_status.duration_seconds = int(duration.total_seconds())
        update_status.save()

        # Update manifest statistics
        calculate_rollout_statistics.delay(update_status.manifest.id)

        return Response({'status': 'marked as success'})

    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """Mark update as failed"""
        update_status = self.get_object()

        update_status.state = 'FAILED'
        update_status.completed_at = timezone.now()
        update_status.error_message = request.data.get('error', 'Unknown error')
        update_status.save()

        # Update manifest statistics
        calculate_rollout_statistics.delay(update_status.manifest.id)

        # Check if auto-rollback should be triggered
        if update_status.manifest.rollback_safe:
            from .tasks import trigger_gateway_rollback
            trigger_gateway_rollback.delay(update_status.id)

        return Response({'status': 'marked as failed'})


class UpdateCheckView(APIView):
    """Check for updates (called by gateways)"""

    def get(self, request):
        gateway_id = request.query_params.get('gateway_id')
        current_version = request.query_params.get('current_version')

        if not gateway_id or not current_version:
            return Response(
                {'error': 'gateway_id and current_version required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find latest compatible update
        manifests = OTAManifest.objects.filter(
            status__in=['STAGED', 'ROLLING_OUT', 'COMPLETED']
        ).order_by('-release_date')

        for manifest in manifests:
            # Check version compatibility
            if self._is_version_compatible(current_version, manifest.min_gateway_version, manifest.max_gateway_version):
                # Check if gateway already has this update
                existing = GatewayUpdateStatus.objects.filter(
                    gateway_id=gateway_id,
                    manifest=manifest,
                    state__in=['SUCCESS', 'APPLYING']
                ).exists()

                if not existing:
                    return Response({
                        'update_available': True,
                        'version': manifest.version,
                        'description': manifest.description,
                        'critical': manifest.critical,
                        'manifest_url': manifest.manifest_url,
                        'signature_url': manifest.signature_url
                    })

        return Response({'update_available': False})

    def _is_version_compatible(
        self,
        gateway_version: str,
        min_version: str,
        max_version: str
    ) -> bool:
        """Check version compatibility"""

        from packaging import version

        try:
            gateway = version.parse(gateway_version)
            minimum = version.parse(min_version)
            maximum = version.parse(max_version)

            return minimum <= gateway <= maximum
        except:
            return True


class UpdateSuccessView(APIView):
    """Report successful update"""

    def post(self, request):
        gateway_id = request.data.get('gateway_id')
        version = request.data.get('version')

        if not gateway_id or not version:
            return Response(
                {'error': 'gateway_id and version required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            manifest = OTAManifest.objects.get(version=version)
            update_status = GatewayUpdateStatus.objects.get(
                gateway_id=gateway_id,
                manifest=manifest
            )

            # Mark as success
            update_status.state = 'SUCCESS'
            update_status.completed_at = timezone.now()
            if update_status.started_at:
                duration = update_status.completed_at - update_status.started_at
                update_status.duration_seconds = int(duration.total_seconds())
            update_status.save()

            # Update manifest stats
            calculate_rollout_statistics.delay(manifest.id)

            return Response({'status': 'success recorded'})

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UpdateFailureView(APIView):
    """Report update failure"""

    def post(self, request):
        gateway_id = request.data.get('gateway_id')
        version = request.data.get('version')
        error = request.data.get('error')

        if not gateway_id or not version:
            return Response(
                {'error': 'gateway_id and version required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            manifest = OTAManifest.objects.get(version=version)
            update_status = GatewayUpdateStatus.objects.get(
                gateway_id=gateway_id,
                manifest=manifest
            )

            # Mark as failed
            update_status.state = 'FAILED'
            update_status.completed_at = timezone.now()
            update_status.error_message = error
            update_status.save()

            # Update manifest stats
            calculate_rollout_statistics.delay(manifest.id)

            # Check if rollback needed
            if manifest.rollback_safe:
                from .tasks import trigger_gateway_rollback
                trigger_gateway_rollback.delay(update_status.id)

            return Response({'status': 'failure recorded'})

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
