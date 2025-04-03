from django.db import models

# Create your models here.

class GuestCustomer(models.Model):
    """
    Model representing a guest customer with temporary session
    """
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Guest customer (Session: {self.session_id})"
    
    class Meta:
        ordering = ['-last_activity']

class GuestAddress(models.Model):
    """
    Model representing a temporary address for guest customers
    """
    guest_customer = models.ForeignKey(GuestCustomer, on_delete=models.CASCADE, related_name='addresses')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.address_line1}, {self.city}"
    
    class Meta:
        ordering = ['id']
