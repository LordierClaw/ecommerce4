from rest_framework import serializers
from .models import Laptop

class LaptopSerializer(serializers.ModelSerializer):
    """
    Serializer for the Laptop model
    """
    class Meta:
        model = Laptop
        fields = '__all__'
        
    def validate_processor_speed(self, value):
        """Validate processor speed is reasonable"""
        if value <= 0 or value > 10:  # Current reasonable range for GHz
            raise serializers.ValidationError("Processor speed must be between 0 and 10 GHz")
        return value
        
    def validate_ram(self, value):
        """Validate RAM is reasonable"""
        if value <= 0 or value > 512:  # Current reasonable range for GB
            raise serializers.ValidationError("RAM must be between 0 and 512 GB")
        return value
        
    def validate_storage_capacity(self, value):
        """Validate storage capacity is reasonable"""
        if value <= 0 or value > 20000:  # Current reasonable range for GB
            raise serializers.ValidationError("Storage capacity must be between 0 and 20000 GB")
        return value 