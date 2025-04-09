from rest_framework import serializers
from .models import RegisteredCustomer, RegisteredAddress, RegisteredActivity

class RegisteredAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for registered customer addresses
    """
    class Meta:
        model = RegisteredAddress
        fields = [
            'id', 'original_id', 'customer', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country', 'address_type',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class RegisteredActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for registered customer activities
    """
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = RegisteredActivity
        fields = [
            'id', 'customer', 'activity_type', 'activity_type_display',
            'description', 'ip_address', 'user_agent', 'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']

class RegisteredCustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for registered customers
    """
    addresses = RegisteredAddressSerializer(many=True, read_only=True)
    latest_activities = serializers.SerializerMethodField()
    
    class Meta:
        model = RegisteredCustomer
        fields = [
            'id', 'original_id', 'username', 'email', 'first_name', 'last_name',
            'registration_date', 'last_login', 'is_active', 'preferences',
            'addresses', 'latest_activities'
        ]
        read_only_fields = ['id', 'registration_date', 'addresses', 'latest_activities']
        
    def get_latest_activities(self, obj):
        """Get the 5 most recent activities"""
        activities = obj.activities.all()[:5]
        return RegisteredActivitySerializer(activities, many=True).data

class RegisteredCustomerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating registered customers
    """
    class Meta:
        model = RegisteredCustomer
        fields = [
            'original_id', 'username', 'email', 'first_name', 'last_name',
            'last_login', 'is_active', 'preferences'
        ] 