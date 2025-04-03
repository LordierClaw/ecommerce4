from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Cart operations
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    def get_queryset(self):
        """Filter carts by customer_id if provided"""
        queryset = Cart.objects.all()
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id is not None:
            queryset = queryset.filter(customer_id=customer_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """
        Add an item to the cart
        """
        cart = self.get_object()
        
        # Get parameters from request
        item_id = request.data.get('item_id')
        item_type = request.data.get('item_type')
        quantity = int(request.data.get('quantity', 1))
        
        if not item_id or not item_type:
            return Response(
                {"error": "Missing required fields: item_id and item_type are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Fetch item details from the appropriate service
        item_url = settings.SERVICE_URLS.get(f"{item_type}s", "") + item_id + "/"
        try:
            response = requests.get(item_url)
            if response.status_code != 200:
                return Response(
                    {"error": f"Item not found: {response.status_code}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            item_data = response.json()
            price = Decimal(item_data.get('price', 0))
            
            # Add or update item in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item_id=item_id,
                item_type=item_type,
                defaults={'quantity': quantity, 'price_at_addition': price}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data)
            
        except requests.RequestException as e:
            return Response(
                {"error": f"Error fetching item details: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def update_item(self, request, pk=None):
        """
        Update the quantity of an item in the cart
        """
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not item_id:
            return Response(
                {"error": "Missing required field: item_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, item_id=item_id)
            
            if quantity <= 0:
                cart_item.delete()
                return Response({"message": "Item removed from cart"})
            
            cart_item.quantity = quantity
            cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data)
            
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        """
        Remove an item from the cart
        """
        cart = self.get_object()
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response(
                {"error": "Missing required field: item_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, item_id=item_id)
            cart_item.delete()
            return Response({"message": "Item removed from cart"})
            
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """
        Clear all items from the cart
        """
        cart = self.get_object()
        cart.items.all().delete()
        return Response({"message": "Cart cleared"})
    
    @action(detail=False, methods=['get'])
    def for_customer(self, request):
        """
        Get the cart for a specific customer
        """
        customer_id = request.query_params.get('customer_id')
        
        if not customer_id:
            return Response(
                {"error": "Missing required parameter: customer_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart, created = Cart.objects.get_or_create(customer_id=customer_id)
        return Response(self.get_serializer(cart).data)
