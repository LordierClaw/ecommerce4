from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Clothes
from .serializers import ClothesSerializer

class ClothesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the Clothes model providing CRUD operations and additional endpoints
    """
    queryset = Clothes.objects.all()
    serializer_class = ClothesSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'brand', 'material', 'style', 'fit', 'primary_color']
    ordering_fields = ['price', 'created_at', 'brand']
    
    @action(detail=False, methods=['get'])
    def brands(self, request):
        """
        Return a list of unique clothing brands
        """
        brands = Clothes.objects.values_list('brand', flat=True).distinct()
        return Response(list(brands))
    
    @action(detail=False, methods=['get'])
    def by_gender(self, request):
        """
        Get clothes filtered by gender
        """
        gender = request.query_params.get('gender', None)
        
        if not gender:
            return Response({"error": "Gender parameter is required"}, status=400)
        
        clothes = self.queryset.filter(gender__iexact=gender)
        serializer = self.get_serializer(clothes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get clothes filtered by category
        """
        category = request.query_params.get('category', None)
        
        if not category:
            return Response({"error": "Category parameter is required"}, status=400)
        
        clothes = self.queryset.filter(category__iexact=category)
        serializer = self.get_serializer(clothes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_size(self, request):
        """
        Get clothes filtered by available size
        """
        size = request.query_params.get('size', None)
        
        if not size:
            return Response({"error": "Size parameter is required"}, status=400)
        
        # Query clothes where the given size is in the available_sizes array
        clothes = []
        for item in self.queryset.all():
            if size in item.available_sizes:
                clothes.append(item)
                
        serializer = self.get_serializer(clothes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_color(self, request):
        """
        Get clothes filtered by color
        """
        color = request.query_params.get('color', None)
        
        if not color:
            return Response({"error": "Color parameter is required"}, status=400)
        
        # Search in both primary and secondary colors
        clothes_by_color = self.queryset.filter(
            Q(primary_color__icontains=color) | 
            Q(secondary_color__icontains=color)
        )
        
        # Also check color_variants
        variants_matches = []
        for item in self.queryset.all():
            if any(color.lower() in variant.lower() for variant in item.color_variants):
                variants_matches.append(item.id)
        
        # Add variant matches that weren't already found
        additional_matches = self.queryset.filter(id__in=variants_matches).exclude(
            Q(primary_color__icontains=color) | 
            Q(secondary_color__icontains=color)
        )
        
        # Combine querysets
        clothes_by_color = (clothes_by_color | additional_matches).distinct()
        
        serializer = self.get_serializer(clothes_by_color, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_material(self, request):
        """
        Get clothes by material
        """
        material = request.query_params.get('material', None)
        
        if not material:
            return Response({"error": "Material parameter is required"}, status=400)
        
        # Search in material field
        clothes = self.queryset.filter(material__icontains=material)
        
        # Also check composition keys (materials)
        composition_matches = []
        for item in self.queryset.all():
            if any(material.lower() in mat.lower() for mat in item.composition.keys()):
                composition_matches.append(item.id)
        
        # Add composition matches that weren't already found
        additional_matches = self.queryset.filter(id__in=composition_matches).exclude(material__icontains=material)
        
        # Combine querysets
        clothes = (clothes | additional_matches).distinct()
        
        serializer = self.get_serializer(clothes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_season(self, request):
        """
        Get clothes by season
        """
        season = request.query_params.get('season', None)
        
        if not season:
            return Response({"error": "Season parameter is required"}, status=400)
        
        clothes = self.queryset.filter(season__icontains=season)
        serializer = self.get_serializer(clothes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """
        Get clothes that are on sale (have a discount)
        """
        clothes = self.queryset.filter(discount_percentage__gt=0)
        serializer = self.get_serializer(clothes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def outfit_recommendation(self, request):
        """
        Get outfit recommendations based on category and color
        """
        base_category = request.query_params.get('category', None)
        base_color = request.query_params.get('color', None)
        
        if not base_category or not base_color:
            return Response({"error": "Both category and color parameters are required"}, status=400)
        
        # Find complementary categories based on the base category
        complementary_categories = {
            'tops': ['pants', 'jeans', 'skirts'],
            'shirts': ['pants', 'jeans', 'skirts'],
            'tshirts': ['pants', 'jeans', 'shorts'],
            'dresses': ['jackets', 'accessories'],
            'pants': ['tops', 'shirts', 'tshirts'],
            'jeans': ['tops', 'shirts', 'tshirts'],
            'shorts': ['tops', 'tshirts'],
            'skirts': ['tops', 'shirts'],
            'jackets': ['dresses', 'tops', 'shirts', 'tshirts', 'pants', 'jeans'],
            'coats': ['dresses', 'tops', 'shirts', 'tshirts', 'pants', 'jeans'],
            'sweaters': ['pants', 'jeans', 'skirts'],
            'hoodies': ['pants', 'jeans', 'shorts'],
        }
        
        # Get items from the base category and color
        base_items = self.queryset.filter(
            category__iexact=base_category,
            primary_color__icontains=base_color
        )
        
        # Get recommended items from complementary categories
        recommended_items = []
        if base_category in complementary_categories:
            for comp_category in complementary_categories[base_category]:
                # Add items from complementary categories
                recommended_items.extend(
                    self.queryset.filter(category__iexact=comp_category)[:3]
                )
        
        # Construct the response with base items and recommendations
        base_serializer = self.get_serializer(base_items, many=True)
        recommended_serializer = self.get_serializer(recommended_items, many=True)
        
        return Response({
            'base_items': base_serializer.data,
            'recommended_items': recommended_serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """
        Get clothes that are in stock
        """
        # A product is in stock if it's available and has any stock quantity entries greater than 0
        in_stock_items = []
        for item in self.queryset.filter(is_available=True):
            if any(qty > 0 for qty in item.stock_quantity.values()):
                in_stock_items.append(item)
                
        serializer = self.get_serializer(in_stock_items, many=True)
        return Response(serializer.data)
