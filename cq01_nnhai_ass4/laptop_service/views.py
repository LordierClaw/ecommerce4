from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response

# Create your views here.
class LaptopViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"message": "Laptop service is under maintenance"})
    
    def retrieve(self, request, pk=None):
        return Response({"message": "Laptop service is under maintenance", "id": pk})
