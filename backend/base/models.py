from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone

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
    paidAt = models.DateTimeField(null=True, blank=True)
    # Xendit returns this ID after we create the hosted checkout invoice.
    # We keep it so webhook events can be matched back to our local order.
    xendit_invoice_id = models.CharField(max_length=255, blank=True, default='')
    # external_id is our own unique reference sent to Xendit.
    # It is safer for reconciliation because we control the value.
    xendit_external_id = models.CharField(max_length=255, blank=True, default='', db_index=True)
    # Store the latest Xendit status we have seen, such as PENDING, PAID, or EXPIRED.
    xendit_status = models.CharField(max_length=50, blank=True, default='PENDING')

    def mark_paid(self):
        """Mark this payment as paid, create order items from the user's cart,
        and clear the user's cart. This operation is atomic and idempotent.
        """
        if self.isPaid:
            return

        carts = cartUser.objects.filter(user=self.user)
        with transaction.atomic():
            for c in carts:
                orderItem.objects.create(
                    product=c.product,
                    payment=self,
                    qty=c.qty,
                    price=c.product.product_price,
                )
            carts.delete()
            self.isPaid = True
            self.paidAt = timezone.now()
            self.save()

class orderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    payment = models.ForeignKey(paymentMethod, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places= 2)


class shippingAddress(models.Model):
    paymentId = models.ForeignKey(paymentMethod, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postalCode = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
