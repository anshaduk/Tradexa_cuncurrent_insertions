from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from core.models import User,Product,Order
import concurrent.futures
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run concurrent database insertions and display results'

    def handle(self,*args,**kwargs):
        user_data = [
           {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
            {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
            {'id': 3, 'name': 'Charlie', 'email': 'charlie@example.com'},
            {'id': 4, 'name': 'David', 'email': 'david@example.com'},
            {'id': 5, 'name': 'Eve', 'email': 'eve@example.com'},
            {'id': 6, 'name': 'Frank', 'email': 'frank@example.com'},
            {'id': 7, 'name': 'Grace', 'email': 'grace@example.com'},
            {'id': 8, 'name': 'Alice', 'email': 'alice@example.com'},
            {'id': 9, 'name': 'Henry', 'email': 'henry@example.com'},
            {'id': 10, 'name': '', 'email': 'jane@example.com'},  
        ]

        product_data = [
            {'id': 1, 'name': 'Laptop', 'price': 1000.00},
            {'id': 2, 'name': 'Smartphone', 'price': 700.00},
            {'id': 3, 'name': 'Headphones', 'price': 150.00},
            {'id': 4, 'name': 'Monitor', 'price': 300.00},
            {'id': 5, 'name': 'Keyboard', 'price': 50.00},
            {'id': 6, 'name': 'Mouse', 'price': 30.00},
            {'id': 7, 'name': 'Laptop', 'price': 1000.00},
            {'id': 8, 'name': 'Smartwatch', 'price': 250.00},
            {'id': 9, 'name': 'Gaming Chair', 'price': 500.00},
            {'id': 10, 'name': 'Earbuds', 'price': -50.00}, 
        ]

        order_data = [
            {'id': 1, 'user_id': 1, 'product_id': 1, 'quantity': 2},
            {'id': 2, 'user_id': 2, 'product_id': 2, 'quantity': 1},
            {'id': 3, 'user_id': 3, 'product_id': 3, 'quantity': 5},
            {'id': 4, 'user_id': 4, 'product_id': 4, 'quantity': 1},
            {'id': 5, 'user_id': 5, 'product_id': 5, 'quantity': 3},
            {'id': 6, 'user_id': 6, 'product_id': 6, 'quantity': 4},
            {'id': 7, 'user_id': 7, 'product_id': 7, 'quantity': 2},
            {'id': 8, 'user_id': 8, 'product_id': 8, 'quantity': 0},
            {'id': 9, 'user_id': 9, 'product_id': 1, 'quantity': -1},
            {'id': 10, 'user_id': 10, 'product_id': 11, 'quantity': 2},
        ]

        def validate_and_prepare_user_data(data):
            valid_users = []
            for item in data:
                try:
                    user = User(id=item['id'],name=item['name'],email=item['email'])
                    user.clean()
                    valid_users.append(user)
                except ValidationError as e:
                    logger.error(f"User validation error: {e} for data {item}")
            return valid_users
        
        def validate_and_prepare_product_data(data):
            valiad_products = []
            for item in data:
                try:
                    product = Product(id=item['id'],name=item['name'],price=item['price'])
                    product.clean()
                    valiad_products.append(product)
                except ValidationError as e:
                    logger.error(f"Product validation error: {e} for data {item}")
            return valiad_products
        
        def validate_and_prepare_order_data(data):
            valid_orders = []
            for item in data:
                try:
                    order = Order(id=item['id'],user_id=item['user_id'],product_id=item['product_id'],quantity=item['quantity'])
                    order.clean()
                    valid_orders.append(order)
                except ValidationError as e:
                    logger.error(f"Order validation error: {e} for data {item}")
            return valid_orders
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            user_future = executor.submit(validate_and_prepare_user_data,user_data)
            product_future =  executor.submit(validate_and_prepare_product_data,product_data)
            order_future = executor.submit(validate_and_prepare_order_data,order_data)

            valid_users = user_future.result()
            valid_products = product_future.result()
            valid_orders = order_future.result()

            User.objects.bulk_create(valid_users,ignore_conflicts=True)
            Product.objects.bulk_create(valid_products,ignore_conflicts=True)
            Order.objects.bulk_create(valid_orders,ignore_conflicts=True)

        self.stdout.write(f"Inserted {len(valid_users)} users, {len(valid_products)} products, and {len(valid_orders)} orders.") 

            
        