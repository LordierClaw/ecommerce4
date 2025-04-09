import requests
import logging
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Customer, Address
from .serializers import CustomerSerializer, AddressSerializer

# Setup logging
logger = logging.getLogger(__name__)

# Service URLs
GUEST_SERVICE_URL = "http://localhost:8010/api/guests"
REGISTERED_SERVICE_URL = "http://localhost:8011/api/registered"
VIP_SERVICE_URL = "http://localhost:8012/api/vip-members"

class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer operations
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'customer_type']
    ordering_fields = ['username', 'date_joined', 'loyalty_points']
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """
        Register a new customer
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        
        # Automatically log in the user
        if 'password' in request.data:
            login(request, customer)
            
        # Create a cart for the new customer
        try:
            requests.post(
                'http://localhost:8003/api/carts/',
                json={'customer_id': customer.id}
            )
        except requests.RequestException:
            # Continue even if cart creation fails
            logger.warning(f"Failed to create cart for customer {customer.id}")
        
        # Register in the specialized service for registered customers
        try:
            # Send relevant data to specialized service
            registered_customer_data = {
                'original_id': customer.id,
                'username': customer.username,
                'email': customer.email,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'date_joined': customer.date_joined.isoformat() if customer.date_joined else None,
            }
            
            requests.post(
                f"{REGISTERED_SERVICE_URL}/",
                json=registered_customer_data
            )
        except requests.RequestException as e:
            logger.warning(f"Failed to register customer in specialized service: {str(e)}")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        Login endpoint
        """
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {"error": "Both username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    @action(detail=True, methods=['post'])
    def add_address(self, request, pk=None):
        """
        Add a new address to a customer
        """
        customer = self.get_object()
        
        # Check if this is a default address
        is_default = request.data.get('is_default', False)
        address_type = request.data.get('address_type', 'both')
        
        # If setting as default, unset other default addresses of the same type
        if is_default:
            if address_type in ['both', 'shipping']:
                Address.objects.filter(
                    customer=customer, 
                    address_type__in=['both', 'shipping'],
                    is_default=True
                ).update(is_default=False)
                
            if address_type in ['both', 'billing']:
                Address.objects.filter(
                    customer=customer, 
                    address_type__in=['both', 'billing'],
                    is_default=True
                ).update(is_default=False)
        
        # Create the address
        data = request.data.copy()
        data['customer'] = customer.id
        
        serializer = AddressSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        address = serializer.save()
        
        # Update address in specialized service based on customer type
        if customer.customer_type == 'vip':
            self._sync_address_with_service(
                address, 
                f"{VIP_SERVICE_URL}/{customer.id}/addresses/",
                customer.id
            )
        elif customer.customer_type == 'registered':
            self._sync_address_with_service(
                address, 
                f"{REGISTERED_SERVICE_URL}/{customer.id}/addresses/",
                customer.id
            )
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _sync_address_with_service(self, address, service_url, customer_id):
        """
        Sync address data with specialized customer service
        """
        try:
            address_data = {
                'original_id': address.id,
                'customer_id': customer_id,
                'address_line1': address.address_line1,
                'address_line2': address.address_line2,
                'city': address.city,
                'state': address.state,
                'postal_code': address.postal_code,
                'country': address.country,
                'address_type': address.address_type,
                'is_default': address.is_default
            }
            
            requests.post(service_url, json=address_data)
        except requests.RequestException as e:
            logger.warning(f"Failed to sync address with specialized service: {str(e)}")
    
    @action(detail=True, methods=['get'])
    def addresses(self, request, pk=None):
        """
        Get all addresses for a customer
        """
        customer = self.get_object()
        addresses = customer.addresses.all()
        
        # Filter by type if requested
        address_type = request.query_params.get('type')
        if address_type:
            if address_type == 'shipping':
                addresses = addresses.filter(address_type__in=['shipping', 'both'])
            elif address_type == 'billing':
                addresses = addresses.filter(address_type__in=['billing', 'both'])
        
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_type(self, request, pk=None):
        """
        Update customer type (admin only)
        """
        customer = self.get_object()
        customer_type = request.data.get('customer_type')
        
        if not customer_type:
            return Response(
                {"error": "Customer type is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save old type to check for changes
        old_type = customer.customer_type
        
        # Update customer type
        customer.customer_type = customer_type
        customer.save()
        
        # Handle upgrade to VIP
        if old_type != 'vip' and customer_type == 'vip':
            try:
                # Register in VIP service
                vip_data = {
                    'customer_id': customer.id,
                    'level': 'silver'  # Default level for new VIP customers
                }
                
                requests.post(f"{VIP_SERVICE_URL}/register/", json=vip_data)
            except requests.RequestException as e:
                logger.warning(f"Failed to register customer as VIP: {str(e)}")
        
        serializer = self.get_serializer(customer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_loyalty_points(self, request, pk=None):
        """
        Add loyalty points to a customer
        """
        customer = self.get_object()
        points = request.data.get('points', 0)
        
        try:
            points = int(points)
            if points <= 0:
                return Response(
                    {"error": "Points must be a positive integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            customer.loyalty_points += points
            customer.save()
            
            # Update points in VIP service if customer is VIP
            if customer.customer_type == 'vip':
                try:
                    requests.post(
                        f"{VIP_SERVICE_URL}/{customer.id}/add_points/",
                        json={'points': points}
                    )
                except requests.RequestException as e:
                    logger.warning(f"Failed to update VIP loyalty points: {str(e)}")
            
            serializer = self.get_serializer(customer)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Points must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    @action(detail=False, methods=['get'])
    def guest_customers(self, request):
        """
        Get all guest customers from the guest customer service
        """
        try:
            response = requests.get(GUEST_SERVICE_URL)
            if response.status_code == 200:
                guests_data = response.json()
                
                # Transform and return guest data
                for guest in guests_data:
                    # Add customer_type for consistency
                    guest['customer_type'] = 'guest'
                    
                return Response(guests_data)
            else:
                logger.error(f"Failed to fetch guest customers: {response.status_code}")
                return Response(
                    {"error": "Failed to fetch guest customers"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except requests.RequestException as e:
            logger.error(f"Error communicating with guest service: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def vip_customers(self, request):
        """
        Get all VIP customers with their membership details
        """
        try:
            # First get local VIP customers
            vip_customers = Customer.objects.filter(customer_type='vip')
            customers_serializer = self.get_serializer(vip_customers, many=True)
            vip_data = customers_serializer.data
            
            # Now get VIP memberships data
            membership_response = requests.get(VIP_SERVICE_URL)
            if membership_response.status_code == 200:
                memberships = membership_response.json()
                
                # Create a dict for easy lookup
                membership_dict = {m['customer_id']: m for m in memberships}
                
                # Merge data
                for customer in vip_data:
                    if customer['id'] in membership_dict:
                        customer['membership'] = membership_dict[customer['id']]
            
            return Response(vip_data)
        except requests.RequestException as e:
            logger.error(f"Error fetching VIP data: {str(e)}")
            # Return local data even if VIP service is unavailable
            customers_serializer = self.get_serializer(
                Customer.objects.filter(customer_type='vip'),
                many=True
            )
            return Response(customers_serializer.data)
    
    @action(detail=False, methods=['get'])
    def all_customers(self, request):
        """
        Get all customers from all sources (local, guest, registered, VIP)
        """
        all_customers = []
        
        # Get local registered customers
        registered_customers = Customer.objects.filter(customer_type='registered')
        registered_serializer = self.get_serializer(registered_customers, many=True)
        all_customers.extend(registered_serializer.data)
        
        # Get local VIP customers
        vip_customers = Customer.objects.filter(customer_type='vip')
        vip_serializer = self.get_serializer(vip_customers, many=True)
        vip_customer_data = vip_serializer.data
        
        # Try to add VIP membership details
        try:
            membership_response = requests.get(VIP_SERVICE_URL)
            if membership_response.status_code == 200:
                memberships = membership_response.json()
                membership_dict = {m['customer_id']: m for m in memberships}
                
                for customer in vip_customer_data:
                    if customer['id'] in membership_dict:
                        customer['membership'] = membership_dict[customer['id']]
        except requests.RequestException:
            logger.error("Error fetching VIP membership details")
            
        all_customers.extend(vip_customer_data)
        
        # Try to get guest customers
        try:
            guest_response = requests.get(GUEST_SERVICE_URL)
            if guest_response.status_code == 200:
                guests = guest_response.json()
                for guest in guests:
                    guest['customer_type'] = 'guest'
                    all_customers.append(guest)
        except requests.RequestException:
            logger.error("Error fetching guest customers")
            
        return Response(all_customers)
    
    @action(detail=True, methods=['get'])
    def vip_benefits(self, request, pk=None):
        """
        Get VIP benefits for a customer if they are a VIP
        """
        customer = self.get_object()
        
        if customer.customer_type != 'vip':
            return Response(
                {"error": "Customer is not a VIP member"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Get customer's VIP level first
            membership_response = requests.get(f"{VIP_SERVICE_URL}/by_customer/?customer_id={customer.id}")
            
            if membership_response.status_code != 200:
                return Response(
                    {"error": "Could not find VIP membership details"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            membership = membership_response.json()
            level = membership.get('level', 'silver')
            
            # Now get benefits for this level
            benefits_response = requests.get(f"{VIP_SERVICE_URL}/benefits/by_level/?level={level}")
            
            if benefits_response.status_code == 200:
                return Response({
                    'membership': membership,
                    'benefits': benefits_response.json()
                })
            else:
                return Response(
                    {"error": "Failed to fetch VIP benefits"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except requests.RequestException as e:
            logger.error(f"Error communicating with VIP service: {str(e)}")
            return Response(
                {"error": "VIP service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=True, methods=['post'])
    def convert_from_guest(self, request, pk=None):
        """
        Convert a guest customer to a registered customer
        """
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {"error": "Guest session ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        customer = self.get_object()
        
        try:
            # Call guest service to convert guest to registered
            conversion_response = requests.post(
                f"{GUEST_SERVICE_URL}/{session_id}/convert_to_registered/",
                json={
                    'customer_id': customer.id,
                    'username': customer.username,
                    'email': customer.email
                }
            )
            
            if conversion_response.status_code == 200:
                return Response({
                    'message': 'Guest converted to registered successfully',
                    'customer': self.get_serializer(customer).data
                })
            else:
                return Response(
                    {"error": "Failed to convert guest account", "details": conversion_response.json()},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except requests.RequestException as e:
            logger.error(f"Error communicating with guest service: {str(e)}")
            return Response(
                {"error": "Guest service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class AddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Address operations
    """
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    
    def get_queryset(self):
        """Filter addresses by customer_id if provided"""
        queryset = Address.objects.all()
        customer_id = self.request.query_params.get('customer_id')
        
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
            
        return queryset
    
    def perform_update(self, serializer):
        """Handle default address logic when updating"""
        address = self.get_object()
        is_default = serializer.validated_data.get('is_default')
        customer = address.customer
        
        # If setting as default, handle other default addresses
        if is_default:
            address_type = serializer.validated_data.get('address_type', address.address_type)
            
            if address_type in ['both', 'shipping']:
                Address.objects.filter(
                    customer=customer, 
                    address_type__in=['both', 'shipping'],
                    is_default=True
                ).exclude(id=address.id).update(is_default=False)
                
            if address_type in ['both', 'billing']:
                Address.objects.filter(
                    customer=customer, 
                    address_type__in=['both', 'billing'],
                    is_default=True
                ).exclude(id=address.id).update(is_default=False)
        
        # Save the changes
        updated_address = serializer.save()
        
        # Sync with specialized services if needed
        if customer.customer_type == 'vip' or customer.customer_type == 'registered':
            customer_viewset = CustomerViewSet()
            service_url = f"{VIP_SERVICE_URL}/{customer.id}/addresses/" if customer.customer_type == 'vip' else f"{REGISTERED_SERVICE_URL}/{customer.id}/addresses/"
            customer_viewset._sync_address_with_service(updated_address, service_url, customer.id)
            
        return updated_address
