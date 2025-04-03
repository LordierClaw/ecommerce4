from django.db import models

# Create your models here.

class Order(models.Model):
    """
    Model representing a customer order
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]
    
    customer_id = models.IntegerField()
    customer_type = models.CharField(max_length=20, default='registered')  # guest, registered, vip
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Addresses
    shipping_address = models.JSONField()  # Snapshot of address
    billing_address = models.JSONField()  # Snapshot of billing address
    
    # Payment information
    payment_method = models.CharField(max_length=50)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Shipping information
    shipping_method = models.CharField(max_length=50)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Pricing
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Delivery details
    delivery_date = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} ({self.status})"
    
    class Meta:
        ordering = ['-order_date']

class OrderItem(models.Model):
    """
    Model representing an item in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_id = models.CharField(max_length=24)
    item_type = models.CharField(max_length=50)  # Type of item (book, laptop, mobile, clothes)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"OrderItem #{self.id} (Order #{self.order.id}, {self.item_type} #{self.item_id})"
    
    class Meta:
        ordering = ['id']
