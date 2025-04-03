from django.urls import path
from . import views

urlpatterns = [
    # Frontend web routes
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('products/', views.product_list_view, name='product_list'),
    path('products/<str:category>/', views.product_list_view, name='product_list_category'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    
    # API Gateway routes
    path('api/<str:service>/', views.GatewayView.as_view(), name='gateway'),
    path('api/<str:service>/<int:pk>/', views.GatewayView.as_view(), name='gateway_with_pk'),
] 