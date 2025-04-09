from rest_framework import serializers
from .models import Clothes

class ClothesSerializer(serializers.ModelSerializer):
    """
    Serializer for the Clothes model
    """
    sale_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Clothes
        fields = '__all__'
        
    def get_sale_price(self, obj):
        """Get the sale price after discount"""
        return obj.get_sale_price()
    
    def validate_available_sizes(self, value):
        """Validate that sizes are provided in a list format"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Available sizes must be a list")
        if not value:
            raise serializers.ValidationError("At least one size must be provided")
        return value
        
    def validate_composition(self, value):
        """Validate composition percentages sum to 100%"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Composition must be a dictionary")
        
        total_percentage = sum(value.values())
        if total_percentage != 100:
            raise serializers.ValidationError("Material composition percentages must sum to 100%")
        return value
        
    def validate_stock_quantity(self, value):
        """Validate stock quantity format"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Stock quantity must be a dictionary mapping size:color to quantity")
        
        for key, qty in value.items():
            if ':' not in key:
                raise serializers.ValidationError(f"Key '{key}' must be in 'size:color' format")
            
            if not isinstance(qty, int) or qty < 0:
                raise serializers.ValidationError(f"Quantity for '{key}' must be a non-negative integer")
        
        return value
        
    def validate_discount_percentage(self, value):
        """Validate discount percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount percentage must be between 0 and 100")
        return value 