from django.db import models

class Shipping(models.Model):
    """
    Model representing a shipping instance for an order
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('failed', 'Failed'),
    ]
    
    CARRIER_CHOICES = [
        ('fedex', 'FedEx'),
        ('ups', 'UPS'),
        ('usps', 'USPS'),
        ('dhl', 'DHL'),
        ('other', 'Other'),
    ]
    
    order_id = models.IntegerField()
    customer_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    carrier = models.CharField(max_length=20, choices=CARRIER_CHOICES, default='other')
    shipping_method = models.CharField(max_length=50, default='standard')
    shipping_address = models.TextField()
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Shipping #{self.id} (Order #{self.order_id}, {self.status})"
    
    class Meta:
        ordering = ['-created_at']
