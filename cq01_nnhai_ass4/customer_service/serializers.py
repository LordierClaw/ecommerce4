from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Customer, Address

class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for customer addresses
    """
    class Meta:
        model = Address
        fields = ['id', 'address_type', 'address_line1', 'address_line2', 
                 'city', 'state', 'postal_code', 'country', 'is_default']
                 
class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for customers
    """
    addresses = AddressSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'customer_type', 'phone', 'date_of_birth', 'loyalty_points', 
                 'preferences', 'addresses', 'password', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True},
            'loyalty_points': {'read_only': True},
            'customer_type': {'read_only': True}
        }
    
    def validate_password(self, value):
        """Validate password using Django's validators"""
        validate_password(value)
        return value
        
    def create(self, validated_data):
        """Create a new customer with encrypted password"""
        password = validated_data.pop('password', None)
        customer = Customer.objects.create(**validated_data)
        
        if password:
            customer.set_password(password)
            customer.save()
            
        return customer
        
    def update(self, instance, validated_data):
        """Update customer and handle password changes"""
        password = validated_data.pop('password', None)
        
        # Update customer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        # Update password if provided
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance 