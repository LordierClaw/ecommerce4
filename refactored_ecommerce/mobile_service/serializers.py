from rest_framework import serializers
from .models import Mobile

class MobileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Mobile model
    """
    class Meta:
        model = Mobile
        fields = '__all__'
        
    def validate_battery_capacity(self, value):
        """Validate battery capacity is reasonable"""
        if value <= 0 or value > 10000:  # Current reasonable range for mAh
            raise serializers.ValidationError("Battery capacity must be between 0 and 10000 mAh")
        return value
        
    def validate_screen_size(self, value):
        """Validate screen size is reasonable"""
        if value <= 0 or value > 8.0:  # Current reasonable range for inches
            raise serializers.ValidationError("Screen size must be between 0 and 8.0 inches")
        return value
        
    def validate_ram(self, value):
        """Validate RAM is reasonable"""
        if value <= 0 or value > 32:  # Current reasonable range for GB
            raise serializers.ValidationError("RAM must be between 0 and 32 GB")
        return value
        
    def validate_storage(self, value):
        """Validate storage is reasonable"""
        if value <= 0 or value > 1024:  # Current reasonable range for GB
            raise serializers.ValidationError("Storage must be between 0 and 1024 GB")
        return value 