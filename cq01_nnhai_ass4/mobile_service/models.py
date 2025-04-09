from django.db import models

class Mobile(models.Model):
    """
    Model representing a mobile device in the store
    """
    NETWORK_TYPES = [
        ('2g', '2G'),
        ('3g', '3G'),
        ('4g', '4G'),
        ('5g', '5G'),
    ]
    
    OS_TYPES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('windows', 'Windows'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    
    # Performance
    processor = models.CharField(max_length=100)
    ram = models.IntegerField()  # GB
    storage = models.IntegerField()  # GB
    expandable_storage = models.BooleanField(default=False)
    max_expandable_storage = models.IntegerField(null=True, blank=True)  # GB
    
    # Display
    screen_size = models.DecimalField(max_digits=3, decimal_places=1)  # inches
    resolution = models.CharField(max_length=50)  # e.g., 1080x2400
    display_type = models.CharField(max_length=50)  # e.g., AMOLED, IPS LCD
    refresh_rate = models.IntegerField(default=60)  # Hz
    
    # Camera
    rear_cameras = models.JSONField()  # e.g., [{"mp": 48, "type": "wide"}, {"mp": 12, "type": "ultrawide"}]
    front_cameras = models.JSONField()  # e.g., [{"mp": 12, "type": "selfie"}]
    video_recording = models.CharField(max_length=50)  # e.g., 4K@60fps
    
    # Battery
    battery_capacity = models.IntegerField()  # mAh
    fast_charging = models.BooleanField(default=False)
    wireless_charging = models.BooleanField(default=False)
    
    # Connectivity
    network_type = models.CharField(max_length=10, choices=NETWORK_TYPES)
    has_wifi = models.BooleanField(default=True)
    has_bluetooth = models.BooleanField(default=True)
    has_nfc = models.BooleanField(default=False)
    has_infrared = models.BooleanField(default=False)
    
    # Physical
    dimensions = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=5, decimal_places=1)  # grams
    water_resistance_rating = models.CharField(max_length=10, null=True, blank=True)  # e.g., IP68
    
    # OS
    operating_system = models.CharField(max_length=50, choices=OS_TYPES)
    os_version = models.CharField(max_length=50)
    
    # Features
    fingerprint_sensor = models.BooleanField(default=False)
    face_recognition = models.BooleanField(default=False)
    stereo_speakers = models.BooleanField(default=False)
    headphone_jack = models.BooleanField(default=False)
    
    # Business details
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    image_url = models.URLField()
    is_available = models.BooleanField(default=True)
    warranty_period = models.IntegerField()  # months
    color_variants = models.JSONField()  # e.g., ["black", "white", "blue"]
    description = models.TextField()
    
    # Timestamps
    release_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.brand} {self.name} ({self.ram}GB RAM, {self.storage}GB, {self.screen_size}\")"
        
    class Meta:
        ordering = ['brand', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['brand']),
            models.Index(fields=['price']),
            models.Index(fields=['ram']),
            models.Index(fields=['storage']),
            models.Index(fields=['network_type']),
        ]
