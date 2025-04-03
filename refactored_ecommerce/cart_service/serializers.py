from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items
    """
    class Meta:
        model = CartItem
        fields = ['id', 'item_id', 'item_type', 'quantity', 'price_at_addition', 'added_at']

class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for shopping carts with nested items
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'created_at', 'updated_at', 'items', 'total_price']
    
    def get_total_price(self, obj):
        """Calculate the total price of all items in the cart"""
        return sum(item.price_at_addition * item.quantity for item in obj.items.all()) 