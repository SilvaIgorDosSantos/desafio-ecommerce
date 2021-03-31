from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.email}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} unidades em estoque com preço unitário de R${self.price})"

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ordem {self.id} feita pelo cliente {self.customer.username}"

class OrdersProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="details")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ordem {self.order.id} - {self.product.name} (Quantidade solicitada: {self.quantity})"