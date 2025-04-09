from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuestCustomerViewSet, GuestAddressViewSet

router = DefaultRouter()
router.register(r'guests', GuestCustomerViewSet)
router.register(r'guest-addresses', GuestAddressViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 