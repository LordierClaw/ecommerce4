from django.db import models
from datetime import datetime, timedelta

# Create your models here.

class VipMembership(models.Model):
    """
    Model representing a VIP membership level
    """
    MEMBERSHIP_LEVELS = [
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond'),
    ]
    
    customer_id = models.IntegerField(unique=True)
    level = models.CharField(max_length=20, choices=MEMBERSHIP_LEVELS, default='silver')
    points = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_level_display()} VIP (Customer #{self.customer_id})"
    
    class Meta:
        ordering = ['-level', '-points']
        
    def save(self, *args, **kwargs):
        # Set default expiration date if not provided
        if not self.expires_at:
            self.expires_at = datetime.now() + timedelta(days=365)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if the membership is expired"""
        return self.expires_at < datetime.now()
    
    @property
    def days_until_expiry(self):
        """Calculate days until membership expires"""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)

class VipBenefit(models.Model):
    """
    Model representing a VIP benefit
    """
    BENEFIT_TYPES = [
        ('discount', 'Discount'),
        ('free_shipping', 'Free Shipping'),
        ('gift', 'Free Gift'),
        ('early_access', 'Early Access'),
        ('cashback', 'Cashback'),
        ('exclusive', 'Exclusive Product'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    benefit_type = models.CharField(max_length=20, choices=BENEFIT_TYPES)
    applicable_level = models.CharField(max_length=20, choices=VipMembership.MEMBERSHIP_LEVELS)
    discount_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_applicable_level_display()} benefit)"
    
    class Meta:
        ordering = ['applicable_level', 'name']

class VipTransaction(models.Model):
    """
    Model representing a VIP point transaction
    """
    TRANSACTION_TYPES = [
        ('earn', 'Points Earned'),
        ('redeem', 'Points Redeemed'),
        ('expire', 'Points Expired'),
        ('adjust', 'Points Adjusted'),
    ]
    
    membership = models.ForeignKey(VipMembership, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    reference_id = models.CharField(max_length=100, blank=True, null=True)  # For order or other reference
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.points} points"
    
    class Meta:
        ordering = ['-created_at']
