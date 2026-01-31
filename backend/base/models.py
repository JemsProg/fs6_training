from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=255)
    description = models.TextField()
    countInStock = models.IntegerField()
    image = models.ImageField(upload_to='products_images/')
    createdAt = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.product_name
    
class cartUser(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qty = models.IntegerField()
    createdAt = models.DateField(auto_now_add=True)
    
class paymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2)
    isPaid = models.BooleanField(default=False)
    paidAt = models.DateField(auto_now_add=True)
    paymongopayment = models.CharField(max_length=255)
    paymongostatus = models.CharField(max_length=255)

class orderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    payment = models.ForeignKey(paymentMethod, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places= 2)


class shippingAddress(models.Model):
    paymentId = models.ForeignKey(User, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postalCode = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
