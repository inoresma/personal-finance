import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .models import Goal
from .serializers import GoalSerializer

logger = logging.getLogger(__name__)


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['goal_type', 'is_active', 'category']
    pagination_class = StandardPagination
    
    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).select_related('category').order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        logger.info(f'Goal created: user={self.request.user.id}, type={serializer.validated_data.get("goal_type")}')
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        goals = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(goals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        goals = self.get_queryset().filter(is_active=True)
        completed_goals = [g for g in goals if g.is_completed]
        serializer = self.get_serializer(completed_goals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        goal = self.get_object()
        goal.is_active = not goal.is_active
        goal.save()
        serializer = self.get_serializer(goal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        goal = self.get_object()
        return Response({
            'current_amount': float(goal.current_amount),
            'target_amount': float(goal.target_amount),
            'progress_percentage': goal.progress_percentage,
            'is_completed': goal.is_completed,
            'days_remaining': goal.days_remaining
        })

