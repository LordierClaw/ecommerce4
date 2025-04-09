from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShippingViewSet

router = DefaultRouter()
router.register(r'', ShippingViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 