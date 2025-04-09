from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Book
from .serializers import BookSerializer

# Create your views here.

class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the Book model providing CRUD operations and additional endpoints
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'isbn', 'genre']
    ordering_fields = ['title', 'author', 'price', 'published_date']
    
    @action(detail=False, methods=['get'])
    def genres(self, request):
        """
        Return a list of unique book genres
        """
        genres = Book.objects.values_list('genre', flat=True).distinct()
        return Response(list(genres))
    
    @action(detail=False, methods=['get'])
    def by_author(self, request):
        """
        Get books filtered by author
        """
        author = request.query_params.get('author', None)
        if author:
            books = Book.objects.filter(author__icontains=author)
            serializer = self.get_serializer(books, many=True)
            return Response(serializer.data)
        return Response({"error": "Author parameter is required"}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_isbn(self, request):
        """
        Get a book by its ISBN
        """
        isbn = request.query_params.get('isbn', None)
        if isbn:
            book = get_object_or_404(Book, isbn=isbn)
            serializer = self.get_serializer(book)
            return Response(serializer.data)
        return Response({"error": "ISBN parameter is required"}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_genre(self, request):
        """
        Get books filtered by genre
        """
        genre = request.query_params.get('genre', None)
        if genre:
            books = Book.objects.filter(genre__icontains=genre)
            serializer = self.get_serializer(books, many=True)
            return Response(serializer.data)
        return Response({"error": "Genre parameter is required"}, status=400)
        
    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """
        Get books that are in stock
        """
        books = Book.objects.filter(is_available=True, stock_quantity__gt=0)
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
