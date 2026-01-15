from django.contrib import admin
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_uah",
                    "price_usd", "in_stock", "top_sale")
    list_filter = ("category", "in_stock", "is_active", "top_sale")
    prepopulated_fields = {"slug": ("name",)}
