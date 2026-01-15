from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_GET
from .models import Category, Product
from cart.cart import Cart


def set_currency(request, code: str):
    code = code.upper()
    allowed = {"UAH", "USD", "EUR"}

    if code in allowed:
        request.session["currency"] = code

        # синхронно оновлюємо ціни в корзині під нову валюту
        Cart(request).update_prices()

    # повертаємось туди, де був користувач
    return redirect(request.META.get("HTTP_REFERER", "shop:catalog_home"))


def catalog_home(request):
    currency = request.session.get("currency", "UAH")
    categories = Category.objects.all()

    top_products = Product.objects.filter(
        is_active=True, top_sale=True).order_by("name")[:6]

    return render(request, "shop/catalog_home.html", {
        "categories": categories,
        "top_products": top_products,
        "currency": currency,
    })


def category_detail(request, slug: str):
    currency = request.session.get("currency", "UAH")
    category = get_object_or_404(Category, slug=slug)

    # якщо є related_name="products":
    products = category.products.all()

    return render(request, "shop/category_detail.html", {
        "category": category,
        "products": products,
        "currency": currency,
    })


def product_detail(request, slug: str):
    currency = request.session.get("currency", "UAH")

    product = get_object_or_404(Product, slug=slug, is_active=True)

    related_products = (
        Product.objects
        .filter(is_active=True, category=product.category)
        .exclude(id=product.id)[:6]
    )

    return render(request, "shop/product_detail.html", {
        "product": product,
        "related_products": related_products,
        "currency": currency,
    })
