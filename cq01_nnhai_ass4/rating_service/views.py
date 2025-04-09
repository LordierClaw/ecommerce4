from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
import requests
import json

from .models import Rating
from .serializers import RatingSerializer, RatingCreateSerializer

class RatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the Rating model
    """
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RatingCreateSerializer
        return RatingSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify that the order exists and belongs to the customer
        # This would typically call the order service API
        try:
            # Sample verification logic - should be expanded in a real implementation
            order_id = serializer.validated_data['order_id']
            customer_id = serializer.validated_data['customer_id']
            item_id = serializer.validated_data['item_id']
            
            # Here you would make an API call to the order service
            # to verify the order belongs to the customer and contains the item
            # order_service_url = f"http://localhost:8000/api/orders/{order_id}/"
            # response = requests.get(order_service_url)
            # if response.status_code != 200:
            #     return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # order_data = response.json()
            # if order_data["customer_id"] != customer_id:
            #     return Response({"error": "This order does not belong to this customer"}, 
            #                     status=status.HTTP_403_FORBIDDEN)
            
            # # Check if the item is in this order
            # item_found = False
            # for item in order_data["items"]:
            #     if item["item_id"] == item_id:
            #         item_found = True
            #         break
            
            # if not item_found:
            #     return Response({"error": "This item is not in the order"}, 
            #                     status=status.HTTP_400_BAD_REQUEST)
            
            # Create the rating
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_item(self, request):
        """
        Get all ratings for a specific item
        """
        item_id = request.query_params.get('item_id')
        item_type = request.query_params.get('item_type')
        
        if not item_id or not item_type:
            return Response({"error": "Both item_id and item_type are required"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        ratings = Rating.objects.filter(item_id=item_id, item_type=item_type)
        serializer = self.get_serializer(ratings, many=True)
        
        # Calculate average rating
        if ratings:
            avg_rating = sum(r.rating for r in ratings) / len(ratings)
        else:
            avg_rating = 0
        
        return Response({
            "average_rating": avg_rating,
            "total_ratings": len(ratings),
            "ratings": serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get all ratings by a specific customer
        """
        customer_id = request.query_params.get('customer_id')
        customer_type = request.query_params.get('customer_type')
        
        if not customer_id or not customer_type:
            return Response({"error": "Both customer_id and customer_type are required"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        ratings = Rating.objects.filter(customer_id=customer_id, customer_type=customer_type)
        serializer = self.get_serializer(ratings, many=True)
        
        return Response(serializer.data) 