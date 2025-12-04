from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Q, Max, Min
from django.db.models.functions import Coalesce

from .models import Bet
from .serializers import BetSerializer, BetListSerializer


class BetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['bet_type', 'result', 'account', 'sport_type']
    search_fields = ['event_name', 'notes']
    ordering_fields = ['date', 'bet_amount', 'net_result', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BetListSerializer
        return BetSerializer
    
    def get_queryset(self):
        return Bet.objects.filter(user=self.request.user).select_related('account')
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        try:
            queryset = self.get_queryset()
            
            total_bet = queryset.aggregate(total=Sum('bet_amount'))['total'] or 0
            
            won_bets = queryset.filter(result='ganó')
            lost_bets = queryset.filter(result='perdió')
            pending_bets = queryset.filter(result='pendiente')
            
            total_won = won_bets.aggregate(total=Sum('payout_amount'))['total'] or 0
            total_lost = lost_bets.aggregate(total=Sum('bet_amount'))['total'] or 0
            
            # El net_result debe ser: total ganado - total apostado
            # Para apuestas ganadas: payout_amount - bet_amount
            # Para apuestas perdidas: -bet_amount
            # Para apuestas pendientes: -bet_amount (aún no se sabe el resultado)
            net_result = total_won - total_bet
            
            roi = 0
            if total_bet > 0:
                roi = ((total_won - total_bet) / total_bet) * 100
            
            total_bets_count = queryset.count()
            won_count = won_bets.count()
            lost_count = lost_bets.count()
            pending_count = pending_bets.count()
            
            win_rate = 0
            if total_bets_count > 0 and (won_count + lost_count) > 0:
                win_rate = (won_count / (won_count + lost_count)) * 100
            
            # Para best_bet, necesitamos calcular net_result manualmente ya que es una propiedad
            # net_result = payout_amount - bet_amount para apuestas ganadas
            # Usamos annotate para calcular la diferencia
            from django.db.models import F
            best_bet = None
            if won_bets.exists():
                best_bet = won_bets.annotate(
                    net_result_calc=F('payout_amount') - F('bet_amount')
                ).order_by('-net_result_calc').first()
            
            worst_bet = lost_bets.order_by('bet_amount').first() if lost_bets.exists() else None
            
            by_type = queryset.values('bet_type').annotate(
                total_bet=Sum('bet_amount'),
                total_won=Sum('payout_amount', filter=Q(result='ganó')),
                count=Count('id')
            ).order_by('-total_bet')
            
            by_result = queryset.values('result').annotate(
                total_bet=Sum('bet_amount'),
                total_payout=Sum('payout_amount'),
                count=Count('id')
            )
            
            return Response({
                'total_bet': float(total_bet),
                'total_won': float(total_won),
                'total_lost': float(total_lost),
                'net_result': float(net_result),
                'roi': round(roi, 2),
                'total_bets': total_bets_count,
                'won_count': won_count,
                'lost_count': lost_count,
                'pending_count': pending_count,
                'win_rate': round(win_rate, 2),
                'best_bet': BetListSerializer(best_bet).data if best_bet else None,
                'worst_bet': BetListSerializer(worst_bet).data if worst_bet else None,
                'by_type': list(by_type),
                'by_result': list(by_result),
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                'error': str(e),
                'total_bet': 0,
                'total_won': 0,
                'total_lost': 0,
                'net_result': 0,
                'roi': 0,
                'total_bets': 0,
                'won_count': 0,
                'lost_count': 0,
                'pending_count': 0,
                'win_rate': 0,
            }, status=500)

