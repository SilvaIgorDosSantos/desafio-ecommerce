from django.contrib import admin
from .models import User, Product, Order, OrdersProduct

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrdersProduct)