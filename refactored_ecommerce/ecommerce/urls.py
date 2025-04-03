"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Gateway Service
    path('', include('gateway_service.urls')),
    
    # API endpoints for each service
    path('api/customers/', include('customer_service.urls')),
    path('api/guest-customers/', include('guest_customer_service.urls')),
    path('api/registered-customers/', include('register_customer_service.urls')),
    path('api/vip-customers/', include('vip_customer_service.urls')),
    path('api/items/', include('items_service.urls')),
    path('api/books/', include('book_service.urls')),
    path('api/laptops/', include('laptop_service.urls')),
    path('api/mobiles/', include('mobile_service.urls')),
    path('api/clothes/', include('clothes_service.urls')),
    path('api/cart/', include('cart_service.urls')),
    path('api/orders/', include('order_service.urls')),
    path('api/payments/', include('paying_service.urls')),
    path('api/shipping/', include('shipping_service.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
