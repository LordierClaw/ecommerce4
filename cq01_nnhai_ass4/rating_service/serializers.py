from rest_framework import serializers
from .models import Rating

class RatingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rating model
    """
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        
class RatingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new rating
    """
    class Meta:
        model = Rating
        fields = ['customer_id', 'customer_type', 'item_id', 'item_type', 'order_id', 'rating', 'comment']
        
    def validate(self, data):
        """
        Validate that a customer can only rate an item from a purchased order
        """
        # Additional validation could be added here to verify order ownership
        # This would typically be done by calling the order service API
        
        # Ensure rating is between 1 and 5
        if data.get('rating') < 1 or data.get('rating') > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars")
            
        return data 