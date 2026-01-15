from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    # для сортування категорій
    order = models.IntegerField(default=0, help_text="Порядок відображення")

    # SEO поля
    meta_description = models.TextField(max_length=160, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ['order', 'name']

    def get_absolute_url(self):
        return reverse("shop:category_detail", args=[self.slug])

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    price_uah = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ціна (₴)",
        validators=[MinValueValidator(0)]
    )
    price_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ціна ($)",
        validators=[MinValueValidator(0)]
    )
    price_eur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ціна (€)",
        validators=[MinValueValidator(0)]
    )

    in_stock = models.BooleanField(default=True, verbose_name="В наявності")
    is_active = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Кількість на складі"
    )
    top_sale = models.BooleanField(default=False, verbose_name="ТОП продажу")

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
        verbose_name="Категорія"
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name="Зображення"
    )

    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Артикул"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    views_count = models.PositiveIntegerField(
        default=0, verbose_name="Переглядів")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ['-created_at']  # Нові товари першими
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'in_stock']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.slug])

    # перевірка наявності
    def is_available(self):
        return self.is_active and self.in_stock and self.stock_quantity > 0

    # отримання ціни в обраній валюті
    def get_price(self, currency='UAH'):
        prices = {
            'UAH': self.price_uah,
            'USD': self.price_usd,
            'EUR': self.price_eur,
        }
        return prices.get(currency.upper(), self.price_uah)


# Модель для додаткових зображень товару
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to="products/gallery/")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Зображення товару"
        verbose_name_plural = "Зображення товарів"

    def __str__(self):
        return f"{self.product.name} - зображення {self.order}"
