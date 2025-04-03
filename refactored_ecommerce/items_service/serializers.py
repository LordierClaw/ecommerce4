from rest_framework import serializers
from .models import Category, Item, ItemImage

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for product categories
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'created_at', 'updated_at']
        
class ItemImageSerializer(serializers.ModelSerializer):
    """
    Serializer for item images
    """
    class Meta:
        model = ItemImage
        fields = ['id', 'item', 'image_url', 'alt_text', 'is_primary', 'order', 'created_at']

class ItemSerializer(serializers.ModelSerializer):
    """
    Serializer for items/products
    """
    images = ItemImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Item
        fields = [
            'id', 'name', 'slug', 'sku', 'description', 'price', 'sale_price', 
            'current_price', 'is_on_sale', 'stock_quantity', 'is_in_stock',
            'category', 'category_name', 'weight', 'dimensions', 'features',
            'status', 'is_featured', 'created_at', 'updated_at', 'images'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
        
    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value
        
    def validate_sale_price(self, value):
        """Validate that sale price is positive and less than regular price"""
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError("Sale price must be greater than zero")
            if 'price' in self.initial_data and value >= float(self.initial_data['price']):
                raise serializers.ValidationError("Sale price must be less than regular price")
        return value

class ItemDetailSerializer(ItemSerializer):
    """
    Detailed serializer for items with complete information
    """
    category = CategorySerializer(read_only=True)
    
    class Meta(ItemSerializer.Meta):
        pass 