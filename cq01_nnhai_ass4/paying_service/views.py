from django.shortcuts import render
import requests
from django.http import JsonResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer

# Create your views here.

class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payment operations
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_id', 'customer_id', 'status', 'transaction_id']
    ordering_fields = ['created_at', 'updated_at', 'amount']

    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        """
        Process a payment for an order
        """
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method')
        payment_details = request.data.get('payment_details', {})
        
        if not order_id or not payment_method:
            return Response(
                {"error": "Missing required fields: order_id and payment_method are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Fetch order details via API
        try:
            order_response = requests.get(f'http://localhost:8004/api/orders/{order_id}/')
            if order_response.status_code != 200:
                return Response(
                    {"error": f"Order not found: {order_response.status_code}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            order_data = order_response.json()
            
            # Create payment record
            payment = Payment.objects.create(
                customer_id=order_data.get('customer_id'),
                customer_type=order_data.get('customer_type', 'registered'),
                order_id=order_id,
                amount=order_data.get('total_price'),
                payment_method=payment_method,
                payment_details=payment_details,
                status='processing'
            )
            
            # Simulate payment processing
            # In a real application, integrate with a payment gateway
            payment.status = 'completed'
            payment.transaction_id = f"txn_{payment.id}_{order_id}"
            payment.save()
            
            # Update order status via API
            requests.patch(
                f'http://localhost:8004/api/orders/{order_id}/update_status/',
                json={'status': 'processing'},
            )
            
            return Response(self.get_serializer(payment).data, status=status.HTTP_201_CREATED)
            
        except requests.RequestException as e:
            return Response(
                {"error": f"Error processing payment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """
        Process a refund for a payment
        """
        payment = self.get_object()
        
        if payment.status != 'completed':
            return Response(
                {"error": "Only completed payments can be refunded"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process refund
        payment.status = 'refunded'
        payment.notes += f"\nRefunded on {payment.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        payment.save()
        
        # Update order status
        try:
            requests.patch(
                f'http://localhost:8004/api/orders/{payment.order_id}/update_status/',
                json={'status': 'returned'},
            )
        except requests.RequestException:
            # Continue even if order update fails
            pass
        
        return Response(self.get_serializer(payment).data)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get payments for a specific customer
        """
        customer_id = request.query_params.get('customer_id')
        
        if not customer_id:
            return Response(
                {"error": "Customer ID parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        payments = self.queryset.filter(customer_id=customer_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def by_order(self, request):
        """
        Get payments for a specific order
        """
        order_id = request.query_params.get('order_id')
        
        if not order_id:
            return Response(
                {"error": "Order ID parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        payments = self.queryset.filter(order_id=order_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
