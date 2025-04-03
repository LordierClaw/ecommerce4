from rest_framework import serializers
from .models import Shipping

class ShippingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Shipping model
    """
    class Meta:
        model = Shipping
        fields = '__all__'
        
    def validate_shipping_cost(self, value):
        """Validate that shipping cost is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Shipping cost cannot be negative")
        return value 