from django.contrib import admin
from .models import Product, Customer, Seller, Order, OrderItem, PlatformApiCall


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "amount", "created_at", "is_deleted")
    list_filter = ("is_deleted",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "mobile", "user", "created_at", "is_deleted")
    search_fields = ("name", "mobile", "user__username")
    list_filter = ("is_deleted",)


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "mobile", "user", "created_at", "is_deleted")
    search_fields = ("name", "mobile", "user__username")
    list_filter = ("is_deleted",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "unit_price", "subtotal")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "seller", "amount", "created_at", "is_deleted")
    search_fields = ("customer__name", "seller__name", "items__product__name")
    list_filter = ("is_deleted",)
    inlines = [OrderItemInline]


@admin.register(PlatformApiCall)
class PlatformApiCallAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "requested_url", "created_at")
    search_fields = ("requested_url", "user__username")
    readonly_fields = ("requested_url", "requested_data", "response_data", "created_at", "updated_at")

# Register your models here.
