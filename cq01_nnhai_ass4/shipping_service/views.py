import requests
from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Shipping
from .serializers import ShippingSerializer
from datetime import datetime, timedelta

class ShippingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Shipping operations
    """
    queryset = Shipping.objects.all()
    serializer_class = ShippingSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_id', 'customer_id', 'status', 'tracking_number']
    ordering_fields = ['created_at', 'estimated_delivery', 'shipping_cost']

    def create(self, request, *args, **kwargs):
        """Create shipping entry with order details"""
        # Add estimated delivery date (5 days from now by default)
        data = request.data.copy()
        
        if 'estimated_delivery' not in data:
            estimated_delivery = datetime.now() + timedelta(days=5)
            data['estimated_delivery'] = estimated_delivery.isoformat()
        
        # If order_id provided, fetch additional details
        order_id = data.get('order_id')
        if order_id and 'customer_id' not in data:
            try:
                # Get order details
                order_response = requests.get(f'http://localhost:8004/api/orders/{order_id}/')
                if order_response.status_code == 200:
                    order_data = order_response.json()
                    data['customer_id'] = order_data.get('customer_id')
                    
                    # Use order's shipping address if not provided
                    if 'shipping_address' not in data and 'shipping_address' in order_data:
                        data['shipping_address'] = str(order_data.get('shipping_address', ''))
            except requests.RequestException:
                pass
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update the status of a shipping entry
        """
        shipping = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response({"error": "Status value is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        shipping.status = status_value
        
        # Set actual delivery date if status is delivered
        if status_value == 'delivered' and not shipping.actual_delivery:
            shipping.actual_delivery = datetime.now()
            
            # Update order status via the order service
            try:
                requests.patch(
                    f'http://localhost:8004/api/orders/{shipping.order_id}/update_status/',
                    json={'status': 'delivered'},
                )
            except requests.RequestException:
                pass
            
        shipping.save()
        return Response(self.get_serializer(shipping).data)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get shipping entries for a specific customer
        """
        customer_id = request.query_params.get('customer_id')
        
        if not customer_id:
            return Response(
                {"error": "Customer ID parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        shipping_entries = self.queryset.filter(customer_id=customer_id)
        serializer = self.get_serializer(shipping_entries, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def by_order(self, request):
        """
        Get shipping entry for a specific order
        """
        order_id = request.query_params.get('order_id')
        
        if not order_id:
            return Response(
                {"error": "Order ID parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        shipping = self.queryset.filter(order_id=order_id).first()
        if not shipping:
            return Response(
                {"error": "No shipping entry found for this order"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = self.get_serializer(shipping)
        return Response(serializer.data)
