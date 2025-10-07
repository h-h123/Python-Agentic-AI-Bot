from flask import current_app
from .cart_service import CartService
from .order_service import OrderService
from .product_service import ProductService
from .user_service import UserService
from .payment_service import PaymentService
from .email_service import EmailService
from .shipping_service import ShippingService

class ServiceManager:
    def __init__(self, app=None):
        self._services = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._services['cart'] = CartService(app)
        self._services['order'] = OrderService(app)
        self._services['product'] = ProductService(app)
        self._services['user'] = UserService(app)
        self._services['payment'] = PaymentService(app)
        self._services['email'] = EmailService(app)
        self._services['shipping'] = ShippingService(app)

    def __getattr__(self, name):
        try:
            return self._services[name]
        except KeyError:
            raise AttributeError(f"No service named {name}")

# Initialize service manager
services = ServiceManager()

def init_services(app):
    services.init_app(app)
    return services