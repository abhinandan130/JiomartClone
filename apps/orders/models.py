from django.db import models
from apps.accounts.models import Customer
from apps.products.models import Product
import uuid


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.full_name} - {self.city}"


class Order(models.Model):
    STATUS_CHOICES = (("pending","Pending"),("paid","Paid"),("shipped","Shipped"),("delivered","Delivered"),("cancelled","Cancelled"))
    PAYMENT_STATUS_CHOICES = (("pending","Pending"),("success","Success"),("failed","Failed"))

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="orders")

    order_number = models.CharField(max_length=100, unique=True, editable=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=30, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self,*args,**kwargs):
        if not self.order_number: self.order_number=f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args,**kwargs)

    def __str__(self): return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self): return f"{self.product.name} ({self.quantity})"
