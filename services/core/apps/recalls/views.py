"""
Recall API views.

Public endpoints (no auth):
    GET /api/v1/recalls/                 — list active recalls, filterable
    GET /api/v1/recalls/{id}/            — recall detail with products

Authenticated endpoints:
    GET  /api/v1/recalls/acknowledgments/                    — list for current user's restaurants
    POST /api/v1/recalls/acknowledgments/                    — create acknowledgment
    PATCH /api/v1/recalls/acknowledgments/{id}/              — update status/notes
"""

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Recall, RecallAcknowledgment
from .serializers import (
    RecallAcknowledgmentSerializer,
    RecallDetailSerializer,
    RecallListSerializer,
)


class RecallListView(generics.ListAPIView):
    """Public list of recalls — cached 15 minutes."""

    permission_classes = [AllowAny]
    serializer_class = RecallListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "recalling_firm", "hazard_type", "products__brand_name"]
    ordering_fields = ["recall_initiation_date", "classification", "status"]
    ordering = ["-recall_initiation_date"]

    def get_queryset(self):
        qs = Recall.objects.prefetch_related("products")

        status_param = self.request.query_params.get("status", "active")
        if status_param != "all":
            qs = qs.filter(status=status_param)

        hazard = self.request.query_params.get("hazard")
        if hazard:
            qs = qs.filter(hazard_type__icontains=hazard)

        state = self.request.query_params.get("state")
        if state:
            qs = qs.filter(affected_states__contains=state.upper())

        source = self.request.query_params.get("source")
        if source:
            qs = qs.filter(source=source)

        return qs

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RecallDetailView(generics.RetrieveAPIView):
    """Public recall detail."""

    permission_classes = [AllowAny]
    serializer_class = RecallDetailSerializer
    queryset = Recall.objects.prefetch_related("products")

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class RecallAcknowledgmentView(APIView):
    """Manage recall acknowledgments for authenticated restaurant operators."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Return acknowledgments for restaurants the user has access to
        user_restaurants = request.user.restaurants.all()
        qs = RecallAcknowledgment.objects.filter(
            restaurant__in=user_restaurants
        ).select_related("recall", "restaurant").order_by("-created_at")

        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        serializer = RecallAcknowledgmentSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RecallAcknowledgmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ack = serializer.save(acknowledged_by=request.user)
        return Response(
            RecallAcknowledgmentSerializer(ack).data,
            status=status.HTTP_201_CREATED,
        )


class RecallAcknowledgmentDetailView(APIView):
    """Update a single acknowledgment."""

    permission_classes = [IsAuthenticated]

    def _get_object(self, pk, user):
        try:
            ack = RecallAcknowledgment.objects.select_related(
                "recall", "restaurant"
            ).get(pk=pk)
        except RecallAcknowledgment.DoesNotExist:
            return None, Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not user.restaurants.filter(pk=ack.restaurant_id).exists():
            return None, Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        return ack, None

    def patch(self, request, pk):
        ack, err = self._get_object(pk, request.user)
        if err:
            return err

        serializer = RecallAcknowledgmentSerializer(ack, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(acknowledged_by=request.user)
        return Response(serializer.data)
