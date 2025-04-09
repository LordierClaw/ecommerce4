from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisteredCustomerViewSet

router = DefaultRouter()
router.register(r'', RegisteredCustomerViewSet, basename='register-customer')

urlpatterns = [
    path('', include(router.urls)),
]