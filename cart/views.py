from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from shop.models import Product
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
        in_stock=True,
    )

    qty = int(request.POST.get("qty", 1))
    cart.add(product=product, qty=qty)
    return redirect(request.META.get("HTTP_REFERER", "cart:detail"))


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:detail")


@require_POST
def cart_increase(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, qty=1)
    return redirect("cart:detail")


@require_POST
def cart_decrease(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    product_id_str = str(product_id)
    if product_id_str in cart.cart:
        if cart.cart[product_id_str]['qty'] > 1:
            cart.cart[product_id_str]['qty'] -= 1
            cart.save()
        else:
            cart.remove(product)

    return redirect("cart:detail")


def checkout(request):
    cart = Cart(request)
    return render(request, "cart/checkout.html", {"cart": cart})
