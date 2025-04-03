from rest_framework import serializers
from .models import VipMembership, VipBenefit, VipTransaction

class VipTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for VIP point transactions
    """
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = VipTransaction
        fields = [
            'id', 'membership', 'transaction_type', 'transaction_type_display',
            'points', 'description', 'created_at', 'reference_id'
        ]
        read_only_fields = ['id', 'created_at']

class VipMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for VIP memberships
    """
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    recent_transactions = serializers.SerializerMethodField()
    
    class Meta:
        model = VipMembership
        fields = [
            'id', 'customer_id', 'level', 'level_display', 'points',
            'joined_at', 'expires_at', 'is_active', 'is_expired',
            'days_until_expiry', 'recent_transactions'
        ]
        read_only_fields = ['id', 'joined_at', 'is_expired', 'days_until_expiry', 'recent_transactions']
    
    def get_recent_transactions(self, obj):
        """Get the 5 most recent transactions"""
        transactions = obj.transactions.all()[:5]
        return VipTransactionSerializer(transactions, many=True).data

class VipMembershipCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating VIP memberships
    """
    class Meta:
        model = VipMembership
        fields = ['customer_id', 'level', 'points', 'expires_at', 'is_active']

class VipBenefitSerializer(serializers.ModelSerializer):
    """
    Serializer for VIP benefits
    """
    benefit_type_display = serializers.CharField(source='get_benefit_type_display', read_only=True)
    applicable_level_display = serializers.CharField(source='get_applicable_level_display', read_only=True)
    
    class Meta:
        model = VipBenefit
        fields = [
            'id', 'name', 'description', 'benefit_type', 'benefit_type_display',
            'applicable_level', 'applicable_level_display', 'discount_value', 'is_active'
        ] 