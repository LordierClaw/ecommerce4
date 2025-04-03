from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model
    """
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'publisher', 
            'published_date', 'description', 'genre', 'language',
            'page_count', 'price', 'cover_image', 'stock_quantity',
            'is_available', 'created_at', 'updated_at'
        ] 