from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Rating(models.Model):
    """
    Model representing a product rating by a customer
    """
    customer_id = models.IntegerField()
    customer_type = models.CharField(max_length=20)  # guest, registered, vip
    item_id = models.CharField(max_length=24)
    item_type = models.CharField(max_length=50)  # Type of item (book, laptop, mobile, clothes)
    order_id = models.IntegerField()  # Link to the order where this item was purchased
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Rating #{self.id} - {self.rating} stars for {self.item_type} #{self.item_id}"
    
    class Meta:
        ordering = ['-created_at']
        # Ensure a customer can only rate an item from a specific order once
        unique_together = ['customer_id', 'customer_type', 'item_id', 'item_type', 'order_id'] 