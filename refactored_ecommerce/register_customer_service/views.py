from django.shortcuts import render
import requests
import logging
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import RegisteredCustomer, RegisteredAddress, RegisteredActivity
from .serializers import (
    RegisteredCustomerSerializer, 
    RegisteredCustomerCreateSerializer,
    RegisteredAddressSerializer, 
    RegisteredActivitySerializer
)

# Setup logging
logger = logging.getLogger(__name__)

# Main customer service URL
CUSTOMER_SERVICE_URL = "http://localhost:8005/customers"

class RegisteredCustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RegisteredCustomer operations
    """
    queryset = RegisteredCustomer.objects.all()
    serializer_class = RegisteredCustomerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'registration_date', 'last_login']
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return RegisteredCustomerCreateSerializer
        return RegisteredCustomerSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new registered customer"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        
        # Create activity record for registration
        RegisteredActivity.objects.create(
            customer=customer,
            activity_type='other',
            description='Customer registered from main service',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            RegisteredCustomerSerializer(customer).data,
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
    
    @action(detail=True, methods=['post'])
    def record_login(self, request, pk=None):
        """Record login activity for a registered customer"""
        customer = self.get_object()
        customer.last_login = timezone.now()
        customer.save()
        
        # Create activity record
        activity = RegisteredActivity.objects.create(
            customer=customer,
            activity_type='login',
            description='Customer logged in',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'status': 'login recorded',
            'customer': RegisteredCustomerSerializer(customer).data,
            'activity': RegisteredActivitySerializer(activity).data
        })
    
    @action(detail=True, methods=['post'])
    def record_activity(self, request, pk=None):
        """Record any customer activity"""
        customer = self.get_object()
        activity_type = request.data.get('activity_type')
        description = request.data.get('description', '')
        metadata = request.data.get('metadata', {})
        
        if not activity_type:
            return Response(
                {"error": "Activity type is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create activity record
        activity = RegisteredActivity.objects.create(
            customer=customer,
            activity_type=activity_type,
            description=description,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata=metadata
        )
        
        return Response(RegisteredActivitySerializer(activity).data)
    
    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Get all activities for a customer"""
        customer = self.get_object()
        activities = customer.activities.all()
        
        # Filter by activity type if requested
        activity_type = request.query_params.get('activity_type')
        if activity_type:
            activities = activities.filter(activity_type=activity_type)
            
        # Pagination
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = RegisteredActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = RegisteredActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_address(self, request, pk=None):
        """Add an address to a registered customer"""
        customer = self.get_object()
        
        # Prepare the address data
        address_data = request.data.copy()
        address_data['customer'] = customer.id
        
        # Check if this is a default address
        is_default = address_data.get('is_default', False)
        address_type = address_data.get('address_type', 'both')
        
        # If setting as default, unset other default addresses of the same type
        if is_default:
            if address_type in ['both', 'shipping']:
                RegisteredAddress.objects.filter(
                    customer=customer, 
                    address_type__in=['both', 'shipping'],
                    is_default=True
                ).update(is_default=False)
                
            if address_type in ['both', 'billing']:
                RegisteredAddress.objects.filter(
                    customer=customer, 
                    address_type__in=['both', 'billing'],
                    is_default=True
                ).update(is_default=False)
        
        # Create the address
        serializer = RegisteredAddressSerializer(data=address_data)
        serializer.is_valid(raise_exception=True)
        address = serializer.save()
        
        # Record activity
        RegisteredActivity.objects.create(
            customer=customer,
            activity_type='profile_update',
            description=f'Added {address_type} address',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def addresses(self, request, pk=None):
        """Get all addresses for a customer"""
        customer = self.get_object()
        addresses = customer.addresses.all()
        
        # Filter by address type if requested
        address_type = request.query_params.get('type')
        if address_type:
            if address_type == 'shipping':
                addresses = addresses.filter(address_type__in=['shipping', 'both'])
            elif address_type == 'billing':
                addresses = addresses.filter(address_type__in=['billing', 'both'])
        
        serializer = RegisteredAddressSerializer(addresses, many=True)
        return Response(serializer.data)
    
class RegisteredAddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RegisteredAddress operations
    """
    queryset = RegisteredAddress.objects.all()
    serializer_class = RegisteredAddressSerializer
    
    def get_queryset(self):
        """Filter addresses by customer_id if provided"""
        queryset = RegisteredAddress.objects.all()
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
                RegisteredAddress.objects.filter(
                    customer=customer, 
                    address_type__in=['both', 'shipping'],
                    is_default=True
                ).exclude(id=address.id).update(is_default=False)
                
            if address_type in ['both', 'billing']:
                RegisteredAddress.objects.filter(
                    customer=customer, 
                    address_type__in=['both', 'billing'],
                    is_default=True
                ).exclude(id=address.id).update(is_default=False)
        
        # Save the updated address
        updated_address = serializer.save()
        
        # Record activity
        RegisteredActivity.objects.create(
            customer=customer,
            activity_type='profile_update',
            description=f'Updated {updated_address.get_address_type_display()} address',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        return updated_address
    
    def perform_destroy(self, instance):
        """Record address deletion activity"""
        customer = instance.customer
        address_type = instance.get_address_type_display()
        
        # Record activity before deletion
        RegisteredActivity.objects.create(
            customer=customer,
            activity_type='profile_update',
            description=f'Deleted {address_type} address',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Delete the address
        instance.delete()

class RegisteredActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for reading RegisteredActivity records
    (Read-only to prevent manual manipulation)
    """
    queryset = RegisteredActivity.objects.all()
    serializer_class = RegisteredActivitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['activity_type', 'description']
    ordering_fields = ['created_at', 'activity_type']
    
    def get_queryset(self):
        """Filter activities by customer_id if provided"""
        queryset = RegisteredActivity.objects.all()
        customer_id = self.request.query_params.get('customer_id')
        
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
            
        return queryset
