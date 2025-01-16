from django.core.exceptions import ValidationError
import re

def validate_email(value):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[azA-Z0-9.-]+\.[a-zA-Z]{2,}$',value):
        raise ValidationError('Invalid email format.')
    
def validate_price(value):
    if value <= 0:
        raise ValidationError('Price must be positive.')
    
def validate_quantity(value):
    if value <= 0:
        raise ValidationError('Quantity must be positive.')
    
    