from django.db import models

# Create your models here.

class RegisteredCustomer(models.Model):
    """
    Model representing a registered customer in the system
    This is a specialized service for registered customer operations
    """
    original_id = models.IntegerField(unique=True, help_text="ID from the main customer service")
    username = models.CharField(max_length=150)
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    preferences = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.username} (ID: {self.original_id})"
    
    class Meta:
        ordering = ['-registration_date']

class RegisteredAddress(models.Model):
    """
    Model representing addresses for registered customers
    """
    ADDRESS_TYPES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('both', 'Both'),
    ]
    
    customer = models.ForeignKey(RegisteredCustomer, on_delete=models.CASCADE, related_name='addresses')
    original_id = models.IntegerField(null=True, blank=True, help_text="ID from the main address model")
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='both')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.address_line1}, {self.city} ({self.get_address_type_display()})"
    
    class Meta:
        ordering = ['-is_default', 'address_type']
        
class RegisteredActivity(models.Model):
    """
    Model for tracking registered customer activities
    """
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('purchase', 'Purchase'),
        ('review', 'Review'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
        ('other', 'Other'),
    ]
    
    customer = models.ForeignKey(RegisteredCustomer, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.customer.username} at {self.created_at}"
    
    class Meta:
        verbose_name_plural = "Registered activities"
        ordering = ['-created_at']
