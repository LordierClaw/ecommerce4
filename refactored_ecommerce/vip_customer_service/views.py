from django.shortcuts import render
import requests
import logging
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VipMembership, VipBenefit, VipTransaction
from .serializers import (
    VipMembershipSerializer, 
    VipMembershipCreateSerializer,
    VipBenefitSerializer, 
    VipTransactionSerializer
)

# Setup logging
logger = logging.getLogger(__name__)

# Main customer service URL
CUSTOMER_SERVICE_URL = "http://localhost:8005/customers"

class VipMembershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for VIP membership operations
    """
    queryset = VipMembership.objects.all()
    serializer_class = VipMembershipSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['level', 'points', 'joined_at', 'expires_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create' or self.action == 'register':
            return VipMembershipCreateSerializer
        return VipMembershipSerializer
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register a customer for VIP membership
        """
        customer_id = request.data.get('customer_id')
        level = request.data.get('level', 'silver')
        
        if not customer_id:
            return Response(
                {"error": "Customer ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check if customer already has a VIP membership
        if VipMembership.objects.filter(customer_id=customer_id).exists():
            return Response(
                {"error": "Customer already has a VIP membership"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Default expiration is 1 year from now
        expires_at = datetime.now() + timedelta(days=365)
        if 'expires_at' in request.data:
            try:
                expires_at = datetime.fromisoformat(request.data['expires_at'])
            except (ValueError, TypeError):
                pass
                
        # Create VIP membership
        membership = VipMembership.objects.create(
            customer_id=customer_id,
            level=level,
            expires_at=expires_at
        )
        
        # Record initial points transaction if starting with points
        points = request.data.get('points', 0)
        if points > 0:
            VipTransaction.objects.create(
                membership=membership,
                transaction_type='earn',
                points=points,
                description='Initial VIP signup points'
            )
        
        # Try to update customer type in customer service
        try:
            requests.patch(
                f"{CUSTOMER_SERVICE_URL}/{customer_id}/update_type/",
                json={'customer_type': 'vip'}
            )
        except requests.RequestException as e:
            logger.warning(f"Failed to update customer type: {str(e)}")
        
        serializer = VipMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get VIP membership for a specific customer
        """
        customer_id = request.query_params.get('customer_id')
        
        if not customer_id:
            return Response(
                {"error": "Customer ID parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            membership = VipMembership.objects.get(customer_id=customer_id)
            serializer = self.get_serializer(membership)
            return Response(serializer.data)
        except VipMembership.DoesNotExist:
            return Response(
                {"error": "VIP membership not found for this customer"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def add_points(self, request, pk=None):
        """
        Add points to a VIP membership
        """
        membership = self.get_object()
        points = request.data.get('points', 0)
        description = request.data.get('description', 'Points added')
        reference_id = request.data.get('reference_id')
        
        try:
            points = int(points)
            if points <= 0:
                return Response(
                    {"error": "Points must be a positive integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Add points to membership
            membership.points += points
            
            # Check if customer can be upgraded to a higher level
            if membership.level == 'silver' and membership.points >= 1000:
                membership.level = 'gold'
                description += '. Upgraded to Gold level!'
            elif membership.level == 'gold' and membership.points >= 5000:
                membership.level = 'platinum'
                description += '. Upgraded to Platinum level!'
            elif membership.level == 'platinum' and membership.points >= 10000:
                membership.level = 'diamond'
                description += '. Upgraded to Diamond level!'
                
            membership.save()
            
            # Record transaction
            transaction = VipTransaction.objects.create(
                membership=membership,
                transaction_type='earn',
                points=points,
                description=description,
                reference_id=reference_id
            )
            
            return Response({
                'membership': self.get_serializer(membership).data,
                'transaction': VipTransactionSerializer(transaction).data
            })
        except ValueError:
            return Response(
                {"error": "Points must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def redeem_points(self, request, pk=None):
        """
        Redeem points from a VIP membership
        """
        membership = self.get_object()
        points = request.data.get('points', 0)
        description = request.data.get('description', 'Points redeemed')
        reference_id = request.data.get('reference_id')
        
        try:
            points = int(points)
            if points <= 0:
                return Response(
                    {"error": "Points must be a positive integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Check if membership has enough points
            if membership.points < points:
                return Response(
                    {"error": "Insufficient points available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Deduct points
            membership.points -= points
            membership.save()
            
            # Record transaction
            transaction = VipTransaction.objects.create(
                membership=membership,
                transaction_type='redeem',
                points=points,
                description=description,
                reference_id=reference_id
            )
            
            return Response({
                'membership': self.get_serializer(membership).data,
                'transaction': VipTransactionSerializer(transaction).data
            })
        except ValueError:
            return Response(
                {"error": "Points must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        """
        Extend the expiration date of a VIP membership
        """
        membership = self.get_object()
        days = request.data.get('days', 0)
        
        try:
            days = int(days)
            if days <= 0:
                return Response(
                    {"error": "Extension days must be a positive integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Calculate new expiration date
            current_expiry = membership.expires_at
            new_expiry = current_expiry + timedelta(days=days)
            
            # Update expiration date
            membership.expires_at = new_expiry
            membership.save()
            
            # Record transaction for the extension
            VipTransaction.objects.create(
                membership=membership,
                transaction_type='adjust',
                points=0,
                description=f'Membership extended by {days} days'
            )
            
            serializer = self.get_serializer(membership)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Days must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Get all transactions for a VIP membership
        """
        membership = self.get_object()
        transactions = membership.transactions.all()
        
        # Filter by transaction type if requested
        transaction_type = request.query_params.get('type')
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
            
        # Filter by date range if requested
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                transactions = transactions.filter(created_at__gte=start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                transactions = transactions.filter(created_at__lte=end_date)
            except ValueError:
                pass
            
        # Pagination
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = VipTransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = VipTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

class VipBenefitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for VIP benefit operations
    """
    queryset = VipBenefit.objects.all()
    serializer_class = VipBenefitSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'benefit_type', 'applicable_level']
    ordering_fields = ['name', 'applicable_level', 'discount_value']
    
    @action(detail=False, methods=['get'])
    def by_level(self, request):
        """
        Get benefits available for a specific VIP level
        """
        level = request.query_params.get('level')
        
        if not level:
            return Response(
                {"error": "VIP level parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if level not in dict(VipMembership.MEMBERSHIP_LEVELS):
            return Response(
                {"error": f"Invalid VIP level: {level}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Return all benefits for the requested level and below
        level_order = ['silver', 'gold', 'platinum', 'diamond']
        applicable_levels = level_order[:level_order.index(level) + 1]
        
        benefits = VipBenefit.objects.filter(
            applicable_level__in=applicable_levels,
            is_active=True
        )
        
        serializer = self.get_serializer(benefits, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get benefits available for a specific customer
        """
        customer_id = request.query_params.get('customer_id')
        
        if not customer_id:
            return Response(
                {"error": "Customer ID parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Get customer's VIP membership
            membership = VipMembership.objects.get(customer_id=customer_id, is_active=True)
            
            # Check if membership is expired
            if membership.is_expired:
                return Response(
                    {"error": "VIP membership has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Return all benefits for the customer's level and below
            level_order = ['silver', 'gold', 'platinum', 'diamond']
            applicable_levels = level_order[:level_order.index(membership.level) + 1]
            
            benefits = VipBenefit.objects.filter(
                applicable_level__in=applicable_levels,
                is_active=True
            )
            
            serializer = self.get_serializer(benefits, many=True)
            return Response(serializer.data)
        except VipMembership.DoesNotExist:
            return Response(
                {"error": "Customer does not have an active VIP membership"},
                status=status.HTTP_404_NOT_FOUND
            )

class VipTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for VIP transactions (read-only)
    """
    queryset = VipTransaction.objects.all()
    serializer_class = VipTransactionSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'points', 'transaction_type']
    
    def get_queryset(self):
        """
        Filter transactions by membership_id or customer_id if provided
        """
        queryset = VipTransaction.objects.all()
        membership_id = self.request.query_params.get('membership_id')
        customer_id = self.request.query_params.get('customer_id')
        
        if membership_id:
            queryset = queryset.filter(membership_id=membership_id)
        elif customer_id:
            queryset = queryset.filter(membership__customer_id=customer_id)
            
        return queryset
