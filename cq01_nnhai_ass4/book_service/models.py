from django.db import models

class Book(models.Model):
    """
    Model representing a book in the bookstore
    """
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    publisher = models.CharField(max_length=200)
    published_date = models.DateField()
    description = models.TextField()
    genre = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    page_count = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_image = models.URLField(null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"
        
    class Meta:
        ordering = ['-published_date']
