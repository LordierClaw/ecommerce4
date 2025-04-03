from django.db import models

# Create your models here.

class Payment(models.Model):
    """
    Model representing a payment in the system
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('cryptocurrency', 'Cryptocurrency'),
        ('gift_card', 'Gift Card'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    customer_id = models.IntegerField()
    customer_type = models.CharField(max_length=20, default='registered')  # guest, registered, vip
    order_id = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_details = models.JSONField(default=dict)  # Stores payment method details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Payment {self.id} (Order #{self.order_id}, {self.status})"
    
    class Meta:
        ordering = ['-created_at']
