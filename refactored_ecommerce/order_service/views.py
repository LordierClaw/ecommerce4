from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order operations
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer_id', 'status', 'tracking_number']
    ordering_fields = ['order_date', 'status', 'total_price']
    
    def get_queryset(self):
        """Filter orders by customer_id if provided"""
        queryset = Order.objects.all()
        customer_id = self.request.query_params.get('customer_id', None)
        customer_type = self.request.query_params.get('customer_type', None)
        status = self.request.query_params.get('status', None)
        
        if customer_id is not None:
            queryset = queryset.filter(customer_id=customer_id)
        
        if customer_type is not None:
            queryset = queryset.filter(customer_type=customer_type)
            
        if status is not None:
            queryset = queryset.filter(status=status)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a new order with nested items
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Create order items if included in the request
        items_data = request.data.get('items', [])
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                item_id=item_data.get('item_id'),
                item_type=item_data.get('item_type', 'unknown'),
                quantity=item_data.get('quantity', 1),
                price=item_data.get('price', 0)
            )
        
        # Refresh serializer to include the created items
        serializer = self.get_serializer(order)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Update the status of an order
        """
        order = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value:
            return Response({"error": "Status value is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        order.status = status_value
        order.save()
        
        return Response(self.get_serializer(order).data)
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """
        Get all items for a specific order
        """
        order = self.get_object()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get orders filtered by status
        """
        status_value = request.query_params.get('status')
        
        if not status_value:
            return Response({"error": "Status parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        orders = self.queryset.filter(status=status_value)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get orders for a specific customer
        """
        customer_id = request.query_params.get('customer_id')
        
        if not customer_id:
            return Response({"error": "Customer ID parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        orders = self.queryset.filter(customer_id=customer_id)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
