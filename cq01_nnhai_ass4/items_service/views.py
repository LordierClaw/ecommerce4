from django.shortcuts import render
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
import requests
import logging
from .models import Category, Item, ItemImage
from .serializers import (
    CategorySerializer, 
    ItemSerializer, 
    ItemDetailSerializer, 
    ItemImageSerializer
)

# Setup logging
logger = logging.getLogger(__name__)

# Service URLs
BOOK_SERVICE_URL = "http://localhost:8006/api/books"
LAPTOP_SERVICE_URL = "http://localhost:8007/api/laptops"
MOBILE_SERVICE_URL = "http://localhost:8008/api/mobiles"
CLOTHES_SERVICE_URL = "http://localhost:8009/api/clothes"

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for working with product categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=True, methods=['get'])
    def items(self, request, slug=None):
        """
        Get all items in a category
        """
        category = self.get_object()
        items = Item.objects.filter(
            Q(category=category) | Q(category__parent=category)
        ).filter(status='published')
        
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)

class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for working with product items
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'sku', 'category__name']
    ordering_fields = ['name', 'price', 'created_at', 'stock_quantity']
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return ItemDetailSerializer
        return ItemSerializer
    
    def get_queryset(self):
        """Apply filters to queryset"""
        queryset = Item.objects.all()
        
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(
                Q(category__slug=category) | Q(category__parent__slug=category)
            )
            
        # Filter by price range if provided
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Filter featured items if requested
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() in ['true', '1', 'yes']:
            queryset = queryset.filter(is_featured=True)
            
        # Filter in-stock items if requested
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() in ['true', '1', 'yes']:
            queryset = queryset.filter(stock_quantity__gt=0)
            
        # Filter by sale items if requested
        on_sale = self.request.query_params.get('on_sale')
        if on_sale and on_sale.lower() in ['true', '1', 'yes']:
            queryset = queryset.filter(sale_price__isnull=False)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_stock(self, request, slug=None):
        """
        Add stock to an item
        """
        item = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {"error": "Quantity must be a positive integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            item.stock_quantity += quantity
            item.save()
            
            # Update stock in specialized service if applicable
            self._update_specialized_item_stock(item, quantity, 'add')
            
            return Response(self.get_serializer(item).data)
        except ValueError:
            return Response(
                {"error": "Quantity must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reduce_stock(self, request, slug=None):
        """
        Reduce stock of an item
        """
        item = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {"error": "Quantity must be a positive integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if item.stock_quantity < quantity:
                return Response(
                    {"error": "Insufficient stock available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            item.stock_quantity -= quantity
            
            # Update status if stock becomes zero
            if item.stock_quantity == 0:
                item.status = 'out_of_stock'
                
            item.save()
            
            # Update stock in specialized service if applicable
            self._update_specialized_item_stock(item, quantity, 'reduce')
            
            return Response(self.get_serializer(item).data)
        except ValueError:
            return Response(
                {"error": "Quantity must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _update_specialized_item_stock(self, item, quantity, action):
        """
        Update stock in specialized service based on item category
        """
        category_name = item.category.name.lower() if item.category else ""
        
        # Determine specialized service URL based on category
        service_url = None
        if 'book' in category_name:
            service_url = f"{BOOK_SERVICE_URL}/{item.sku}/update_stock/"
        elif 'laptop' in category_name:
            service_url = f"{LAPTOP_SERVICE_URL}/{item.sku}/update_stock/"
        elif 'mobile' in category_name:
            service_url = f"{MOBILE_SERVICE_URL}/{item.sku}/update_stock/"
        elif 'clothes' in category_name or 'clothing' in category_name:
            service_url = f"{CLOTHES_SERVICE_URL}/{item.sku}/update_stock/"
            
        if service_url:
            try:
                data = {'quantity': quantity, 'action': action}
                response = requests.post(service_url, json=data)
                
                if response.status_code != 200:
                    logger.error(f"Failed to update stock in specialized service: {response.text}")
            except requests.RequestException as e:
                logger.error(f"Error communicating with specialized service: {str(e)}")
            
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured items
        """
        items = Item.objects.filter(is_featured=True, status='published')
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """
        Get items on sale
        """
        items = Item.objects.filter(sale_price__isnull=False, status='published')
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def books(self, request):
        """
        Get books from book service and convert to item format
        """
        try:
            response = requests.get(BOOK_SERVICE_URL)
            if response.status_code == 200:
                books_data = response.json()
                
                # Transform book data to item format
                items_data = []
                for book in books_data:
                    # Map book fields to item fields
                    item_data = {
                        'id': f"book_{book['id']}",
                        'name': book['title'],
                        'sku': book.get('isbn', f"BK{book['id']}"),
                        'description': book.get('description', ''),
                        'price': book.get('price', 0),
                        'stock_quantity': book.get('stock', 0),
                        'category_name': 'Books',
                        'features': {
                            'author': book.get('author', ''),
                            'publisher': book.get('publisher', ''),
                            'pages': book.get('pages', 0),
                            'genre': book.get('genre', ''),
                            'published_date': book.get('published_date', '')
                        }
                    }
                    items_data.append(item_data)
                    
                return Response(items_data)
            else:
                logger.error(f"Failed to fetch books: {response.status_code}")
                return Response({"error": "Failed to fetch books"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            logger.error(f"Error communicating with book service: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def laptops(self, request):
        """
        Get laptops from laptop service and convert to item format
        """
        try:
            response = requests.get(LAPTOP_SERVICE_URL)
            if response.status_code == 200:
                laptops_data = response.json()
                
                # Transform laptop data to item format
                items_data = []
                for laptop in laptops_data:
                    # Map laptop fields to item fields
                    item_data = {
                        'id': f"laptop_{laptop['id']}",
                        'name': laptop.get('name', 'Laptop'),
                        'sku': laptop.get('sku', f"LP{laptop['id']}"),
                        'description': laptop.get('description', ''),
                        'price': laptop.get('price', 0),
                        'stock_quantity': laptop.get('stock', 0),
                        'category_name': 'Laptops',
                        'features': {
                            'brand': laptop.get('brand', ''),
                            'model': laptop.get('model', ''),
                            'processor': laptop.get('processor', ''),
                            'ram': laptop.get('ram', ''),
                            'storage': laptop.get('storage', ''),
                            'display': laptop.get('display', ''),
                            'graphics': laptop.get('graphics', '')
                        }
                    }
                    items_data.append(item_data)
                    
                return Response(items_data)
            else:
                logger.error(f"Failed to fetch laptops: {response.status_code}")
                return Response({"error": "Failed to fetch laptops"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            logger.error(f"Error communicating with laptop service: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def mobiles(self, request):
        """
        Get mobile phones from mobile service and convert to item format
        """
        try:
            response = requests.get(MOBILE_SERVICE_URL)
            if response.status_code == 200:
                mobiles_data = response.json()
                
                # Transform mobile data to item format
                items_data = []
                for mobile in mobiles_data:
                    # Map mobile fields to item fields
                    item_data = {
                        'id': f"mobile_{mobile['id']}",
                        'name': mobile.get('name', 'Mobile Phone'),
                        'sku': mobile.get('sku', f"MB{mobile['id']}"),
                        'description': mobile.get('description', ''),
                        'price': mobile.get('price', 0),
                        'stock_quantity': mobile.get('stock', 0),
                        'category_name': 'Mobile Phones',
                        'features': {
                            'brand': mobile.get('brand', ''),
                            'model': mobile.get('model', ''),
                            'screen_size': mobile.get('screen_size', ''),
                            'camera': mobile.get('camera', ''),
                            'battery': mobile.get('battery', ''),
                            'storage': mobile.get('storage', ''),
                            'os': mobile.get('os', '')
                        }
                    }
                    items_data.append(item_data)
                    
                return Response(items_data)
            else:
                logger.error(f"Failed to fetch mobiles: {response.status_code}")
                return Response({"error": "Failed to fetch mobile phones"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            logger.error(f"Error communicating with mobile service: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def clothes(self, request):
        """
        Get clothes from clothes service and convert to item format
        """
        try:
            response = requests.get(CLOTHES_SERVICE_URL)
            if response.status_code == 200:
                clothes_data = response.json()
                
                # Transform clothes data to item format
                items_data = []
                for clothing in clothes_data:
                    # Map clothing fields to item fields
                    item_data = {
                        'id': f"clothing_{clothing['id']}",
                        'name': clothing.get('name', 'Clothing Item'),
                        'sku': clothing.get('sku', f"CL{clothing['id']}"),
                        'description': clothing.get('description', ''),
                        'price': clothing.get('price', 0),
                        'stock_quantity': clothing.get('stock', 0),
                        'category_name': 'Clothing',
                        'features': {
                            'brand': clothing.get('brand', ''),
                            'size': clothing.get('size', ''),
                            'color': clothing.get('color', ''),
                            'material': clothing.get('material', ''),
                            'gender': clothing.get('gender', ''),
                            'type': clothing.get('type', '')
                        }
                    }
                    items_data.append(item_data)
                    
                return Response(items_data)
            else:
                logger.error(f"Failed to fetch clothes: {response.status_code}")
                return Response({"error": "Failed to fetch clothing items"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            logger.error(f"Error communicating with clothes service: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def all_products(self, request):
        """
        Get all products from all specialized services and local items
        """
        all_items = []
        
        # Get local items
        local_items = Item.objects.filter(status='published')
        local_serializer = self.get_serializer(local_items, many=True)
        all_items.extend(local_serializer.data)
        
        # Fetch from specialized services
        try:
            # Books
            book_response = requests.get(BOOK_SERVICE_URL)
            if book_response.status_code == 200:
                for book in book_response.json():
                    item_data = {
                        'id': f"book_{book['id']}",
                        'name': book.get('title', 'Book'),
                        'sku': book.get('isbn', f"BK{book['id']}"),
                        'description': book.get('description', ''),
                        'price': book.get('price', 0),
                        'stock_quantity': book.get('stock', 0),
                        'category_name': 'Books',
                        'product_type': 'book'
                    }
                    all_items.append(item_data)
        except requests.RequestException:
            logger.error("Error fetching books")
            
        try:
            # Laptops
            laptop_response = requests.get(LAPTOP_SERVICE_URL)
            if laptop_response.status_code == 200:
                for laptop in laptop_response.json():
                    item_data = {
                        'id': f"laptop_{laptop['id']}",
                        'name': laptop.get('name', 'Laptop'),
                        'sku': laptop.get('sku', f"LP{laptop['id']}"),
                        'description': laptop.get('description', ''),
                        'price': laptop.get('price', 0),
                        'stock_quantity': laptop.get('stock', 0),
                        'category_name': 'Laptops',
                        'product_type': 'laptop'
                    }
                    all_items.append(item_data)
        except requests.RequestException:
            logger.error("Error fetching laptops")
            
        try:
            # Mobiles
            mobile_response = requests.get(MOBILE_SERVICE_URL)
            if mobile_response.status_code == 200:
                for mobile in mobile_response.json():
                    item_data = {
                        'id': f"mobile_{mobile['id']}",
                        'name': mobile.get('name', 'Mobile Phone'),
                        'sku': mobile.get('sku', f"MB{mobile['id']}"),
                        'description': mobile.get('description', ''),
                        'price': mobile.get('price', 0),
                        'stock_quantity': mobile.get('stock', 0),
                        'category_name': 'Mobile Phones',
                        'product_type': 'mobile'
                    }
                    all_items.append(item_data)
        except requests.RequestException:
            logger.error("Error fetching mobiles")
            
        try:
            # Clothes
            clothes_response = requests.get(CLOTHES_SERVICE_URL)
            if clothes_response.status_code == 200:
                for clothing in clothes_response.json():
                    item_data = {
                        'id': f"clothing_{clothing['id']}",
                        'name': clothing.get('name', 'Clothing Item'),
                        'sku': clothing.get('sku', f"CL{clothing['id']}"),
                        'description': clothing.get('description', ''),
                        'price': clothing.get('price', 0),
                        'stock_quantity': clothing.get('stock', 0),
                        'category_name': 'Clothing',
                        'product_type': 'clothing'
                    }
                    all_items.append(item_data)
        except requests.RequestException:
            logger.error("Error fetching clothes")
            
        return Response(all_items)
    
    @action(detail=True, methods=['get'])
    def product_details(self, request, slug=None):
        """
        Get detailed product information from the appropriate specialized service
        """
        item = self.get_object()
        category_name = item.category.name.lower() if item.category else ""
        
        # Return local item details if not a specialized product
        if not any(cat in category_name for cat in ['book', 'laptop', 'mobile', 'cloth']):
            serializer = ItemDetailSerializer(item)
            return Response(serializer.data)
        
        # Determine service URL and fetch specialized details
        service_url = None
        if 'book' in category_name:
            service_url = f"{BOOK_SERVICE_URL}/{item.sku}/"
        elif 'laptop' in category_name:
            service_url = f"{LAPTOP_SERVICE_URL}/{item.sku}/"
        elif 'mobile' in category_name:
            service_url = f"{MOBILE_SERVICE_URL}/{item.sku}/"
        elif 'clothes' in category_name or 'clothing' in category_name:
            service_url = f"{CLOTHES_SERVICE_URL}/{item.sku}/"
            
        if service_url:
            try:
                response = requests.get(service_url)
                if response.status_code == 200:
                    specialized_data = response.json()
                    
                    # Merge local item data with specialized data
                    serializer = ItemDetailSerializer(item)
                    item_data = serializer.data
                    item_data['specialized_details'] = specialized_data
                    
                    return Response(item_data)
                else:
                    logger.error(f"Failed to fetch specialized product details: {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Error communicating with specialized service: {str(e)}")
                
        # Return basic item details if specialized fetch fails
        serializer = ItemDetailSerializer(item)
        return Response(serializer.data)

class ItemImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for working with item images
    """
    queryset = ItemImage.objects.all()
    serializer_class = ItemImageSerializer
    
    def get_queryset(self):
        """Filter by item if provided"""
        queryset = ItemImage.objects.all()
        item_id = self.request.query_params.get('item_id')
        
        if item_id:
            queryset = queryset.filter(item_id=item_id)
            
        return queryset
    
    def perform_create(self, serializer):
        """Handle primary image logic when creating"""
        is_primary = serializer.validated_data.get('is_primary', False)
        item = serializer.validated_data.get('item')
        
        # If setting as primary, update other images
        if is_primary:
            ItemImage.objects.filter(item=item, is_primary=True).update(is_primary=False)
            
        serializer.save()
        
    def perform_update(self, serializer):
        """Handle primary image logic when updating"""
        is_primary = serializer.validated_data.get('is_primary', False)
        item = serializer.instance.item
        
        # If setting as primary, update other images
        if is_primary:
            ItemImage.objects.filter(item=item, is_primary=True).exclude(id=serializer.instance.id).update(is_primary=False)
            
        serializer.save()
