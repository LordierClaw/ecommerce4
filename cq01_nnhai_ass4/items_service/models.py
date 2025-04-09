from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    """
    Model representing product categories
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

class Item(models.Model):
    """
    Model representing a product/item in the store
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text='Weight in kg')
    dimensions = models.JSONField(null=True, blank=True, help_text='Product dimensions (length, width, height)')
    features = models.JSONField(null=True, blank=True, help_text='Product features as key-value pairs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        
    @property
    def current_price(self):
        """Return sale price if available, otherwise regular price"""
        return self.sale_price if self.sale_price else self.price
    
    @property
    def is_on_sale(self):
        """Check if item is on sale"""
        return bool(self.sale_price)
    
    @property
    def is_in_stock(self):
        """Check if item is in stock"""
        return self.stock_quantity > 0

class ItemImage(models.Model):
    """
    Model representing images for items
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=255)
    alt_text = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.item.name}"
    
    class Meta:
        ordering = ['order', 'created_at']
