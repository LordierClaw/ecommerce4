from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payment model
    """
    class Meta:
        model = Payment
        fields = '__all__'
        
    def validate_amount(self, value):
        """Validate that amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero")
        return value 