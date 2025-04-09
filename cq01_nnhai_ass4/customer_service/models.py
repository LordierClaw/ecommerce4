from django.db import models
from django.contrib.auth.models import AbstractUser

class Customer(AbstractUser):
    """
    Model representing a customer in the system
    """
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customer_groups',
        related_query_name='customer'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customer_permissions',
        related_query_name='customer'
    )
    
    CUSTOMER_TYPES = [
        ('guest', 'Guest'),
        ('registered', 'Registered'),
        ('vip', 'VIP'),
    ]
    
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='registered')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    loyalty_points = models.IntegerField(default=0)
    preferences = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.username} ({self.get_customer_type_display()})"
    
    class Meta:
        ordering = ['username']

class Address(models.Model):
    """
    Model representing a customer address
    """
    ADDRESS_TYPES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('both', 'Both'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='both')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.country} ({self.get_address_type_display()})"
    
    class Meta:
        ordering = ['-is_default', 'address_type']
