from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction
from core.models import User, Product, Order
import concurrent.futures
import logging
from typing import List, Dict, Tuple, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run concurrent database insertions with detailed error handling'

    def __init__(self):
        super().__init__()
        self.validation_errors = defaultdict(list)
        
    def validate_user(self, user_data: Dict[str, Any], existing_emails: set) -> Tuple[bool, str]:

        if not user_data['name'] or not user_data['name'].strip():
            return False, f"User ID {user_data['id']}: Name is required"
        
        if user_data['email'] in existing_emails:
            return False, f"User ID {user_data['id']}: Duplicate email {user_data['email']}"
        return True, ""

    def validate_product(self, product_data: Dict[str, Any], existing_products: set) -> Tuple[bool, str]:

        if not product_data['name'] or not product_data['name'].strip():
            return False, f"Product ID {product_data['id']}: Name is required"
        
        if float(product_data['price']) <= 0:
            return False, f"Product ID {product_data['id']}: Price must be positive"
        product_key = (product_data['name'], float(product_data['price']))

        if product_key in existing_products:
            return False, f"Product ID {product_data['id']}: Duplicate product {product_data['name']}"
        return True, ""

    def validate_order(self, order_data: Dict[str, Any], valid_user_ids: set, valid_product_ids: set) -> Tuple[bool, str]:

        if order_data['quantity'] <= 0:
            return False, f"Order ID {order_data['id']}: Quantity must be positive"
        
        if order_data['user_id'] not in valid_user_ids:
            return False, f"Order ID {order_data['id']}: Invalid user_id {order_data['user_id']}"
        
        if order_data['product_id'] not in valid_product_ids:
            return False, f"Order ID {order_data['id']}: Invalid product_id {order_data['product_id']}"
        return True, ""

    def prepare_valid_records(self, model_class: type, data: List[Dict[str, Any]]) -> Tuple[List[Any], List[Dict[str, Any]]]:
        
        valid_records = []
        invalid_records = []
        
        
        existing_emails = set(User.objects.values_list('email', flat=True))
        existing_products = set(Product.objects.values_list('name', 'price'))
        valid_user_ids = set(User.objects.values_list('id', flat=True))
        valid_product_ids = set(Product.objects.values_list('id', flat=True))

        for item in data:
            try:
                if model_class == User:
                    is_valid, error_msg = self.validate_user(item, existing_emails)

                    if is_valid:
                        existing_emails.add(item['email'])

                elif model_class == Product:
                    is_valid, error_msg = self.validate_product(item, existing_products)

                    if is_valid:
                        existing_products.add((item['name'], float(item['price'])))
                else:  
                    is_valid, error_msg = self.validate_order(item, valid_user_ids, valid_product_ids)

                if is_valid:
                    record = model_class(**item)
                    valid_records.append(record)
                else:
                    invalid_records.append({'data': item, 'error': error_msg})
                    self.validation_errors[model_class.__name__].append(error_msg)

            except Exception as e:
                error_msg = f"{model_class.__name__} ID {item.get('id')}: Unexpected error - {str(e)}"
                invalid_records.append({'data': item, 'error': error_msg})
                self.validation_errors[model_class.__name__].append(error_msg)

        return valid_records, invalid_records

    @transaction.atomic
    def handle(self, *args, **kwargs):

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
            {'id': 10, 'name': '', 'email': 'jane@example.com'}
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
            {'id': 10, 'name': 'Earbuds', 'price': -50.00}
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
            {'id': 10, 'user_id': 10, 'product_id': 11, 'quantity': 2}
        ]

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            
                user_future = executor.submit(self.prepare_valid_records, User, user_data)
                product_future = executor.submit(self.prepare_valid_records, Product, product_data)

                valid_users, invalid_users = user_future.result()
                valid_products, invalid_products = product_future.result()

                created_users = User.objects.bulk_create(valid_users, ignore_conflicts=True)
                created_products = Product.objects.bulk_create(valid_products, ignore_conflicts=True)

                valid_orders, invalid_orders = self.prepare_valid_records(Order, order_data)
                created_orders = Order.objects.bulk_create(valid_orders, ignore_conflicts=True)


                self.stdout.write(self.style.SUCCESS(
                    f"\nSuccessfully inserted:"
                    f"\n- Users: {len(created_users)} (Failed: {len(invalid_users)})"
                    f"\n- Products: {len(created_products)} (Failed: {len(invalid_products)})"
                    f"\n- Orders: {len(created_orders)} (Failed: {len(invalid_orders)})"
                ))

                
                self.stdout.write("\nValidation Errors:")
                for model_name, errors in self.validation_errors.items():
                    self.stdout.write(f"\n{model_name} Errors:")
                    for error in errors:
                        self.stdout.write(f"- {error}")

        except Exception as e:
            logger.error(f"Fatal error during data insertion: {str(e)}")
            raise