import uuid
import requests
from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import GuestCustomer, GuestAddress
from .serializers import GuestCustomerSerializer, GuestAddressSerializer

class GuestCustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for guest customer operations
    """
    queryset = GuestCustomer.objects.all()
    serializer_class = GuestCustomerSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def create_guest(self, request):
        """
        Create a new guest customer with a unique session ID
        """
        # Generate a unique session ID for the guest
        session_id = str(uuid.uuid4())
        
        # Create the guest customer
        guest = GuestCustomer.objects.create(session_id=session_id)
        
        # Create a cart for the new guest customer
        try:
            requests.post(
                'http://localhost:8003/api/carts/',
                json={'guest_session_id': session_id}
            )
        except requests.RequestException:
            # Continue even if cart creation fails
            pass
        
        serializer = self.get_serializer(guest)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_address(self, request, pk=None):
        """
        Add an address to a guest customer
        """
        guest = self.get_object()
        
        # Prepare address data
        data = request.data.copy()
        data['guest_customer'] = guest.id
        
        serializer = GuestAddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_session(self, request):
        """
        Get guest customer by session ID
        """
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {"error": "Session ID parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            guest = GuestCustomer.objects.get(session_id=session_id)
            serializer = self.get_serializer(guest)
            return Response(serializer.data)
        except GuestCustomer.DoesNotExist:
            return Response(
                {"error": "Guest customer not found with provided session ID"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def convert_to_registered(self, request, pk=None):
        """
        Convert a guest customer to a registered customer
        """
        guest = self.get_object()
        
        # Required fields for creating a registered customer
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {"error": f"Missing required field: {field}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create registered customer via API
        try:
            customer_data = {
                'username': request.data['username'],
                'email': request.data['email'],
                'password': request.data['password'],
                'first_name': request.data.get('first_name', ''),
                'last_name': request.data.get('last_name', ''),
                'phone': request.data.get('phone', ''),
            }
            
            customer_response = requests.post(
                'http://localhost:8005/customers/',
                json=customer_data
            )
            
            if customer_response.status_code != 201:
                return Response(
                    {"error": "Failed to create registered customer", "details": customer_response.json()},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            registered_customer = customer_response.json()
            
            # Transfer guest addresses to registered customer
            for address in guest.addresses.all():
                address_data = {
                    'customer': registered_customer['id'],
                    'address_line1': address.address_line1,
                    'address_line2': address.address_line2,
                    'city': address.city,
                    'state': address.state,
                    'postal_code': address.postal_code,
                    'country': address.country,
                    'address_type': 'both',
                    'is_default': True  # Make first address default
                }
                
                requests.post(
                    f'http://localhost:8005/customers/{registered_customer["id"]}/add_address/',
                    json=address_data
                )
                
            # Transfer cart items from guest to registered customer
            try:
                # Get guest cart
                cart_response = requests.get(
                    f'http://localhost:8003/api/carts/by_session/?session_id={guest.session_id}'
                )
                
                if cart_response.status_code == 200:
                    cart_data = cart_response.json()
                    
                    # If cart has items, transfer them
                    if cart_data and 'items' in cart_data and cart_data['items']:
                        for item in cart_data['items']:
                            requests.post(
                                f'http://localhost:8003/api/carts/add_item/',
                                json={
                                    'customer_id': registered_customer['id'],
                                    'item_id': item['item_id'],
                                    'quantity': item['quantity']
                                }
                            )
                        
                        # Delete guest cart
                        requests.delete(
                            f'http://localhost:8003/api/carts/{cart_data["id"]}/'
                        )
            except requests.RequestException:
                # Continue even if cart transfer fails
                pass
                
            # Delete the guest customer
            guest.delete()
            
            return Response(registered_customer, status=status.HTTP_201_CREATED)
            
        except requests.RequestException as e:
            return Response(
                {"error": f"Error converting to registered customer: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GuestAddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for guest customer addresses
    """
    queryset = GuestAddress.objects.all()
    serializer_class = GuestAddressSerializer
    
    def get_queryset(self):
        """Filter addresses by guest_customer_id if provided"""
        queryset = GuestAddress.objects.all()
        guest_id = self.request.query_params.get('guest_id')
        
        if guest_id:
            queryset = queryset.filter(guest_customer_id=guest_id)
            
        return queryset
