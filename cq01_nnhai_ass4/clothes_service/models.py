from django.db import models

class Clothes(models.Model):
    """
    Model representing a clothing item in the store
    """
    GENDER_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('unisex', 'Unisex'),
        ('children', 'Children'),
    ]
    
    SIZE_SYSTEMS = [
        ('us', 'US'),
        ('eu', 'EU'),
        ('uk', 'UK'),
        ('intl', 'International'),
    ]
    
    CATEGORY_CHOICES = [
        ('tops', 'Tops'),
        ('shirts', 'Shirts'),
        ('tshirts', 'T-Shirts'),
        ('dresses', 'Dresses'),
        ('pants', 'Pants'),
        ('jeans', 'Jeans'),
        ('shorts', 'Shorts'),
        ('skirts', 'Skirts'),
        ('jackets', 'Jackets'),
        ('coats', 'Coats'),
        ('sweaters', 'Sweaters'),
        ('hoodies', 'Hoodies'),
        ('activewear', 'Activewear'),
        ('swimwear', 'Swimwear'),
        ('lingerie', 'Lingerie'),
        ('sleepwear', 'Sleepwear'),
        ('suits', 'Suits'),
        ('socks', 'Socks'),
        ('underwear', 'Underwear'),
        ('accessories', 'Accessories'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    
    # Basic information
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    size_system = models.CharField(max_length=10, choices=SIZE_SYSTEMS, default='us')
    
    # Available sizes - stored as JSON array
    available_sizes = models.JSONField(help_text="e.g., ['S', 'M', 'L', 'XL']")
    
    # Materials and composition
    material = models.CharField(max_length=255, help_text="Primary material, e.g., Cotton, Polyester")
    composition = models.JSONField(help_text="e.g., {'cotton': 80, 'polyester': 20} for 80% cotton, 20% polyester")
    
    # Styling and fit
    style = models.CharField(max_length=100, blank=True)
    fit = models.CharField(max_length=50, blank=True, help_text="e.g., Regular, Slim, Loose, Oversize")
    season = models.CharField(max_length=50, blank=True, help_text="e.g., Summer, Winter, All Seasons")
    
    # Color information
    primary_color = models.CharField(max_length=50)
    secondary_color = models.CharField(max_length=50, blank=True)
    color_variants = models.JSONField(help_text="List of available color options", default=list)
    pattern = models.CharField(max_length=50, blank=True, help_text="e.g., Solid, Striped, Plaid, Floral")
    
    # Care information
    care_instructions = models.TextField(blank=True)
    wash_type = models.CharField(max_length=50, blank=True, help_text="e.g., Machine wash, Hand wash, Dry clean")
    
    # Physical attributes
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in grams")
    origin = models.CharField(max_length=100, blank=True, help_text="Country/region of origin")
    
    # Business information
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    stock_quantity = models.JSONField(help_text="Stock by size and color, e.g., {'S:Red': 10, 'M:Red': 5}")
    sku = models.CharField(max_length=100, unique=True, help_text="Stock Keeping Unit")
    is_available = models.BooleanField(default=True)
    
    # Media
    image_url = models.URLField()
    additional_images = models.JSONField(default=list, help_text="List of additional image URLs")
    
    # Description
    description = models.TextField()
    features = models.JSONField(default=list, help_text="List of product features")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.brand} {self.name} ({self.gender} {self.category})"
        
    def get_sale_price(self):
        """Calculate the sale price after applying discount"""
        if self.discount_percentage > 0:
            return self.price * (1 - (self.discount_percentage / 100))
        return self.price
    
    class Meta:
        ordering = ['brand', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['brand']),
            models.Index(fields=['gender']),
            models.Index(fields=['category']),
            models.Index(fields=['price']),
            models.Index(fields=['primary_color']),
        ]
