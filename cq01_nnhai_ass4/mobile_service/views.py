from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Mobile
from .serializers import MobileSerializer

class MobileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for the Mobile model providing CRUD operations and additional endpoints
    """
    queryset = Mobile.objects.all()
    serializer_class = MobileSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'brand', 'model_number', 'processor']
    ordering_fields = ['price', 'screen_size', 'ram', 'storage']
    
    @action(detail=False, methods=['get'])
    def brands(self, request):
        """
        Return a list of unique mobile brands
        """
        brands = Mobile.objects.values_list('brand', flat=True).distinct()
        return Response(list(brands))
    
    @action(detail=False, methods=['get'])
    def by_os(self, request):
        """
        Get mobile devices filtered by operating system
        """
        os_type = request.query_params.get('os_type', None)
        os_version = request.query_params.get('os_version', None)
        
        if not (os_type or os_version):
            return Response({"error": "OS type or version parameter is required"}, status=400)
        
        query = Q()
        if os_type:
            query |= Q(operating_system__iexact=os_type)
        if os_version:
            query |= Q(os_version__icontains=os_version)
            
        mobiles = self.queryset.filter(query)
        serializer = self.get_serializer(mobiles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_specs(self, request):
        """
        Get mobiles filtered by RAM and storage
        """
        min_ram = request.query_params.get('min_ram', None)
        min_storage = request.query_params.get('min_storage', None)
        
        query = Q()
        
        if min_ram:
            try:
                query &= Q(ram__gte=int(min_ram))
            except ValueError:
                pass
        
        if min_storage:
            try:
                query &= Q(storage__gte=int(min_storage))
            except ValueError:
                pass
        
        mobiles = self.queryset.filter(query)
        serializer = self.get_serializer(mobiles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_camera(self, request):
        """
        Get mobile devices with a minimum camera resolution
        """
        min_mp = request.query_params.get('min_mp', None)
        if not min_mp:
            return Response({"error": "Minimum megapixels parameter is required"}, status=400)
            
        try:
            min_mp = int(min_mp)
            # Need to query JSONField, which is a bit more complex
            # This is a simplified implementation - in a real app, consider using a more robust query
            mobiles = []
            for mobile in self.queryset.all():
                max_mp = 0
                for camera in mobile.rear_cameras:
                    if camera.get('mp', 0) > max_mp:
                        max_mp = camera.get('mp', 0)
                
                if max_mp >= min_mp:
                    mobiles.append(mobile)
                    
            serializer = self.get_serializer(mobiles, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response({"error": "Invalid minimum megapixels value"}, status=400)
    
    @action(detail=False, methods=['get'])
    def with_features(self, request):
        """
        Get mobile devices with specific features
        """
        has_nfc = request.query_params.get('nfc', '').lower() == 'true'
        has_fingerprint = request.query_params.get('fingerprint', '').lower() == 'true'
        has_face_recognition = request.query_params.get('face_recognition', '').lower() == 'true'
        has_wireless_charging = request.query_params.get('wireless_charging', '').lower() == 'true'
        
        query = Q()
        
        if has_nfc:
            query &= Q(has_nfc=True)
        if has_fingerprint:
            query &= Q(fingerprint_sensor=True)
        if has_face_recognition:
            query &= Q(face_recognition=True)
        if has_wireless_charging:
            query &= Q(wireless_charging=True)
            
        mobiles = self.queryset.filter(query)
        serializer = self.get_serializer(mobiles, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """
        Get mobile devices that are in stock
        """
        mobiles = self.queryset.filter(is_available=True, stock_quantity__gt=0)
        serializer = self.get_serializer(mobiles, many=True)
        return Response(serializer.data)
