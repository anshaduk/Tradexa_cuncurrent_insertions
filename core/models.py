from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver
import re

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        app_label = 'core'
        db_table = 'users'
    
    def __str__(self):
        return self.name

    def clean(self):
        if not self.name:
            raise ValidationError('Name is required')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            raise ValidationError('Invalid email format')
        if User.objects.filter(email=self.email).exists():
            raise ValidationError('Email already exists')
        
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10,decimal_places=2)

    class Meta:
        app_label = 'core'
        db_table = 'products'

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name:
            raise ValidationError('Name is required')
        if self.price <= 0:
            raise ValidationError('Price must be positive')
        
class Order(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    quantity = models.IntegerField()

    class Meta:
        app_label = 'core'
        db_table = 'orders'

    def __str__(self):
        return f"Order(user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})"


    def clean(self):
        if self.quantity <= 0:
            raise ValidationError('Quantity must be positive')
        
        if not User.objects.filter(id=self.user_id).exists():
            raise ValidationError(f"User with ID {self.user_id} does not exist")
        
        if not Product.objects.filter(id=self.product_id).exists():
            raise ValidationError(f"Product with ID {self.product_id} does not exist")
        

### Signal to handle User deletion ###

@receiver(post_delete,sender=User)
def delete_orders_for_user(sender,instance,**kwargs):
    Order.objects.filter(user_id=instance.id).delete()

### Signal to handle Product deletion ###

def delete_orders_for_product(sender,instance,**kwargs):
    Order.objects.filter(product_id=instance.id).delete()


        



