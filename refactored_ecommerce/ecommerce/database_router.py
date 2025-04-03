class DatabaseRouter:
    """
    A router to control all database operations on models in the
    different service applications.
    """
    
    def db_for_read(self, model, **hints):
        """
        Attempts to read from the specific database for each app.
        """
        app_label = model._meta.app_label
        
        if app_label == 'guest_customer_service':
            return 'guest_customers'
        elif app_label == 'register_customer_service':
            return 'registered_customers'
        elif app_label == 'vip_customer_service':
            return 'vip_customers'
        elif app_label == 'book_service':
            return 'books'
        elif app_label == 'laptop_service':
            return 'laptops'
        elif app_label == 'mobile_service':
            return 'mobiles'
        elif app_label == 'clothes_service':
            return 'clothes'
        elif app_label == 'items_service':
            return 'items'
        elif app_label in ['cart_service', 'order_service', 'paying_service', 'shipping_service']:
            return 'transactions'
        
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write to the specific database for each app.
        """
        app_label = model._meta.app_label
        
        if app_label == 'guest_customer_service':
            return 'guest_customers'
        elif app_label == 'register_customer_service':
            return 'registered_customers'
        elif app_label == 'vip_customer_service':
            return 'vip_customers'
        elif app_label == 'book_service':
            return 'books'
        elif app_label == 'laptop_service':
            return 'laptops'
        elif app_label == 'mobile_service':
            return 'mobiles'
        elif app_label == 'clothes_service':
            return 'clothes'
        elif app_label == 'items_service':
            return 'items'
        elif app_label in ['cart_service', 'order_service', 'paying_service', 'shipping_service']:
            return 'transactions'
        
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same database or 
        if they are in related services with the same database.
        """
        transaction_apps = ['cart_service', 'order_service', 'paying_service', 'shipping_service']
        
        # Allow relations within the same app
        if obj1._meta.app_label == obj2._meta.app_label:
            return True
            
        # Allow relations between transaction services
        if obj1._meta.app_label in transaction_apps and obj2._meta.app_label in transaction_apps:
            return True
            
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure that each app's models only appear in the
        appropriate database.
        """
        if db == 'guest_customers':
            return app_label == 'guest_customer_service'
        elif db == 'registered_customers':
            return app_label == 'register_customer_service'
        elif db == 'vip_customers':
            return app_label == 'vip_customer_service'
        elif db == 'books':
            return app_label == 'book_service'
        elif db == 'laptops':
            return app_label == 'laptop_service'
        elif db == 'mobiles':
            return app_label == 'mobile_service'
        elif db == 'clothes':
            return app_label == 'clothes_service'
        elif db == 'items':
            return app_label == 'items_service'
        elif db == 'transactions':
            return app_label in ['cart_service', 'order_service', 'paying_service', 'shipping_service']
        elif db == 'default':
            # Allow auth models and other apps to use the default database
            return (
                app_label not in [
                    'guest_customer_service', 'register_customer_service', 'vip_customer_service',
                    'book_service', 'laptop_service', 'mobile_service', 'clothes_service', 
                    'items_service', 'cart_service', 'order_service', 'paying_service', 'shipping_service'
                ]
            )
        
        return None 