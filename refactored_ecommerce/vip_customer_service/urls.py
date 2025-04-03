from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VipMembershipViewSet, VipBenefitViewSet, VipTransactionViewSet

router = DefaultRouter()
router.register(r'memberships', VipMembershipViewSet)
router.register(r'benefits', VipBenefitViewSet)
router.register(r'transactions', VipTransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 