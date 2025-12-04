from rest_framework import serializers
from .models import Bet


class BetSerializer(serializers.ModelSerializer):
    bet_type_display = serializers.CharField(source='get_bet_type_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    sport_type_display = serializers.CharField(source='get_sport_type_display', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    net_result = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_winning = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Bet
        fields = [
            'id', 'bet_type', 'bet_type_display', 'event_name', 'sport_type', 'sport_type_display',
            'bet_amount', 'odds', 'result', 'result_display', 'payout_amount',
            'account', 'account_name', 'date', 'notes', 'net_result', 'is_winning',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'net_result', 'is_winning']
    
    def validate(self, attrs):
        result = attrs.get('result', self.instance.result if self.instance else 'pendiente')
        payout_amount = attrs.get('payout_amount', self.instance.payout_amount if self.instance else 0)
        
        if result == 'ganó' and (not payout_amount or payout_amount <= 0):
            raise serializers.ValidationError({
                'payout_amount': 'El monto ganado es requerido y debe ser mayor a 0 cuando el resultado es "ganó".'
            })
        
        if result != 'ganó' and payout_amount > 0:
            raise serializers.ValidationError({
                'payout_amount': 'El monto ganado solo puede ser mayor a 0 cuando el resultado es "ganó".'
            })
        
        bet_amount = attrs.get('bet_amount', self.instance.bet_amount if self.instance else None)
        if bet_amount and bet_amount <= 0:
            raise serializers.ValidationError({
                'bet_amount': 'El monto apostado debe ser mayor a 0.'
            })
        
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BetListSerializer(serializers.ModelSerializer):
    bet_type_display = serializers.CharField(source='get_bet_type_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    net_result = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_winning = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Bet
        fields = [
            'id', 'bet_type', 'bet_type_display', 'event_name', 'sport_type',
            'bet_amount', 'odds', 'result', 'result_display', 'payout_amount',
            'account_name', 'date', 'net_result', 'is_winning', 'created_at'
        ]



