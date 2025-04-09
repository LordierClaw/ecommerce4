from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items
    """
    class Meta:
        model = OrderItem
        fields = ['id', 'item_id', 'item_type', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for orders with nested items
    """
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'customer_type', 'order_date', 'status', 
                 'shipping_address', 'billing_address', 'payment_method', 'payment_id',
                 'shipping_method', 'shipping_cost', 'tax', 'total_price',
                 'delivery_date', 'tracking_number', 'notes', 'created_at', 'updated_at', 'items'] 