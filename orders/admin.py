from django.contrib import admin
from .models import Dish, Employee, Order, OrderItem

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phonenumber']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table_number', 'status', 'registered_at']
    list_filter = ['status']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'dish', 'quantity', 'price']
