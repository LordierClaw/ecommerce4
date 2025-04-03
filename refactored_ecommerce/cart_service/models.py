from django.db import models

# Create your models here.

class Cart(models.Model):
    """
    Model representing a customer's shopping cart
    """
    customer_id = models.IntegerField()  # Reference to Customer
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart #{self.id} (Customer #{self.customer_id})"
    
    class Meta:
        ordering = ['-created_at']

class CartItem(models.Model):
    """
    Model representing an item in a shopping cart
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item_id = models.CharField(max_length=24)  # MongoDB ObjectId
    item_type = models.CharField(max_length=50)  # Type of item (book, laptop, mobile, clothes)
    quantity = models.IntegerField()
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"CartItem #{self.id} (Item #{self.item_id}, Qty: {self.quantity})"
    
    class Meta:
        ordering = ['-added_at']
