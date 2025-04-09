from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings

# Create your views here.

def login_view(request):
    # If the user is already authenticated, redirect to home or profile
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')

def register_view(request):
    # Handle the registration logic, or just render the registration page
    if request.method == 'POST':
        # Add registration logic here (e.g., saving user data)
        return redirect('login')  # Redirect to login after successful registration
    return render(request, 'register.html')

def profile_view(request):
    # Render the profile page
    if not request.user.is_authenticated:
        return redirect('login')  # If not authenticated, redirect to login
    return render(request, 'profile.html', {'user': request.user})

def home_view(request):
    # Render the home page
    return render(request, 'home.html')

def product_list_view(request, category=None):
    # Render the product list page, optionally filtered by category
    context = {'category': category} if category else {}
    return render(request, 'product_list.html', context)

def product_detail_view(request, product_id):
    # Render the product detail page
    try:
        # Get product info based on the type
        # For simplicity, we'll assume it's in items_service
        item_url = f"{settings.SERVICE_URLS['items']}{product_id}/"
        product_response = requests.get(item_url)
        
        if product_response.status_code != 200:
            return render(request, 'error.html', {'message': 'Product not found'})
        
        product = product_response.json()
        
        # Get product ratings
        ratings_url = f"{settings.SERVICE_URLS.get('ratings', 'http://localhost:8000/api/ratings/')}by_item/"
        ratings_params = {
            'item_id': product_id,
            'item_type': product.get('type', 'item')
        }
        ratings_response = requests.get(ratings_url, params=ratings_params)
        
        if ratings_response.status_code == 200:
            ratings_data = ratings_response.json()
            avg_rating = ratings_data.get('average_rating', 0)
            total_ratings = ratings_data.get('total_ratings', 0)
            ratings = ratings_data.get('ratings', [])
        else:
            avg_rating = 0
            total_ratings = 0
            ratings = []
        
        context = {
            'product': product,
            'avg_rating': avg_rating,
            'total_ratings': total_ratings,
            'ratings': ratings
        }
        
        return render(request, 'product_detail.html', context)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in product_detail_view: {str(e)}")
        return render(request, 'error.html', {'message': 'Error loading product details'})

def cart_view(request):
    # Render the cart page
    return render(request, 'cart.html')

def checkout_view(request):
    # Render the checkout page
    return render(request, 'checkout.html')

def order_detail_view(request, order_id):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        # Get order details
        order_url = f"{settings.SERVICE_URLS['orders']}{order_id}/"
        customer_id = request.user.id  # Assuming user ID is same as customer ID
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-User-ID': str(customer_id)
        }
        
        order_response = requests.get(order_url, headers=headers)
        
        if order_response.status_code != 200:
            return render(request, 'error.html', {'message': 'Order not found or access denied'})
        
        order = order_response.json()
        
        # Verify this order belongs to the current user
        if order.get('customer_id') != customer_id:
            return render(request, 'error.html', {'message': 'You do not have permission to view this order'})
        
        # Get item details for each order item
        order_items = []
        for item in order.get('items', []):
            # Get item info from appropriate service
            item_type = item.get('item_type')
            item_id = item.get('item_id')
            
            # This would be replaced with actual API call to right service based on item_type
            # For simplicity, we'll assume all items are in items_service
            item_url = f"{settings.SERVICE_URLS['items']}{item_id}/"
            item_response = requests.get(item_url)
            
            if item_response.status_code == 200:
                item_data = item_response.json()
                item_data.update({
                    'item_id': item_id,
                    'item_type': item_type,
                    'quantity': item.get('quantity'),
                    'price': item.get('price')
                })
                
                # Check if this item has been rated
                rating_url = f"{settings.SERVICE_URLS.get('ratings', 'http://localhost:8000/api/ratings/')}by-item/"
                rating_params = {
                    'item_id': item_id,
                    'item_type': item_type,
                    'order_id': order_id,
                    'customer_id': customer_id
                }
                rating_response = requests.get(rating_url, params=rating_params)
                
                if rating_response.status_code == 200:
                    ratings = rating_response.json()
                    # Find the rating for this specific order, if it exists
                    for rating in ratings:
                        if rating.get('order_id') == order_id:
                            item_data['rating'] = rating
                            break
                
                order_items.append(item_data)
        
        context = {
            'order': order,
            'order_items': order_items
        }
        
        return render(request, 'order_detail.html', context)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in order_detail_view: {str(e)}")
        return render(request, 'error.html', {'message': 'Error loading order details'})

def submit_rating_view(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method != 'POST':
        return redirect('home')
    
    try:
        # Get form data
        order_id = request.POST.get('order_id')
        item_id = request.POST.get('item_id')
        item_type = request.POST.get('item_type')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        # Validate data
        if not all([order_id, item_id, item_type, rating]):
            return render(request, 'error.html', {'message': 'Missing required rating information'})
        
        # Create rating via API
        rating_url = settings.SERVICE_URLS.get('ratings', 'http://localhost:8000/api/ratings/')
        customer_id = request.user.id  # Assuming user ID is same as customer ID
        
        rating_data = {
            'customer_id': customer_id,
            'customer_type': 'registered',  # Could be dynamic based on user type
            'item_id': item_id,
            'item_type': item_type,
            'order_id': order_id,
            'rating': int(rating),
            'comment': comment
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-User-ID': str(customer_id)
        }
        
        rating_response = requests.post(rating_url, json=rating_data, headers=headers)
        
        if rating_response.status_code in [200, 201]:
            # Successfully submitted rating, redirect back to order detail
            return redirect('order_detail', order_id=order_id)
        else:
            error_message = "Failed to submit rating. "
            if rating_response.status_code == 400:
                try:
                    error_data = rating_response.json()
                    if 'error' in error_data:
                        error_message += error_data['error']
                    elif isinstance(error_data, dict):
                        # Format validation errors
                        for field, errors in error_data.items():
                            if isinstance(errors, list):
                                error_message += f"{field}: {', '.join(errors)} "
                            else:
                                error_message += f"{field}: {errors} "
                except:
                    error_message += "Please check your input."
            
            return render(request, 'error.html', {'message': error_message})
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in submit_rating_view: {str(e)}")
        return render(request, 'error.html', {'message': 'Error submitting rating'})

class GatewayView(APIView):
    # Dictionary mapping service names to their internal URLs
    service_urls = settings.SERVICE_URLS
    
    def _forward_request(self, request, url, pk=None):
        """
        Forward the request to the appropriate service and return the response
        """
        if pk:
            url = f"{url}{pk}/"
            
        method = request.method.lower()
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Copy authentication headers if present
        if 'HTTP_AUTHORIZATION' in request.META:
            headers['Authorization'] = request.META['HTTP_AUTHORIZATION']
        
        # Forward user ID if authenticated
        if request.user.is_authenticated:
            headers['X-User-ID'] = str(request.user.id)
            
            # Add customer type if available
            if hasattr(request.user, 'customer') and hasattr(request.user.customer, 'type'):
                headers['X-Customer-Type'] = request.user.customer.type
        
        try:
            if method == 'get':
                response = requests.get(url, headers=headers, params=request.query_params)
            elif method == 'post':
                response = requests.post(url, json=request.data, headers=headers)
            elif method == 'put':
                response = requests.put(url, json=request.data, headers=headers)
            elif method == 'patch':
                response = requests.patch(url, json=request.data, headers=headers)
            elif method == 'delete':
                response = requests.delete(url, headers=headers)
            else:
                return Response({"error": "Method not allowed"}, status=405)
            
            # Return the service response
            return Response(response.json(), status=response.status_code)
        except requests.RequestException as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error forwarding request to {url}: {str(e)}")
            return Response({"error": "Service unavailable"}, status=503)

    def get(self, request, service, pk=None):
        """Handle GET requests to services"""
        if service not in self.service_urls:
            return Response({"error": f"Unknown service: {service}"}, status=404)
            
        return self._forward_request(request, self.service_urls[service], pk)
        
    def post(self, request, service, pk=None):
        """Handle POST requests to services"""
        if service not in self.service_urls:
            return Response({"error": f"Unknown service: {service}"}, status=404)
            
        return self._forward_request(request, self.service_urls[service], pk)
        
    def put(self, request, service, pk=None):
        """Handle PUT requests to services"""
        if service not in self.service_urls:
            return Response({"error": f"Unknown service: {service}"}, status=404)
            
        return self._forward_request(request, self.service_urls[service], pk)
        
    def patch(self, request, service, pk=None):
        """Handle PATCH requests to services"""
        if service not in self.service_urls:
            return Response({"error": f"Unknown service: {service}"}, status=404)
            
        return self._forward_request(request, self.service_urls[service], pk)
        
    def delete(self, request, service, pk=None):
        """Handle DELETE requests to services"""
        if service not in self.service_urls:
            return Response({"error": f"Unknown service: {service}"}, status=404)
            
        return self._forward_request(request, self.service_urls[service], pk)
