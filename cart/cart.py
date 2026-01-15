from decimal import Decimal
from django.conf import settings
from shop.models import Product


PRICE_FIELD_BY_CURRENCY = {
    "UAH": "price_uah",
    "USD": "price_usd",
    "EUR": "price_eur",
}


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def _get_currency(self):
        return self.session.get("currency", "UAH")

    def _get_price_for_product(self, product, currency: str) -> Decimal:
        field = PRICE_FIELD_BY_CURRENCY.get(currency, "price_uah")
        return getattr(product, field)

    def add(self, product, qty=1, override_qty=False):
        product_id = str(product.id)
        currency = self._get_currency()
        price = self._get_price_for_product(product, currency)

        if product_id not in self.cart:
            self.cart[product_id] = {
                "qty": 0,
                "price": str(price),
                "currency": currency,
            }

        # якщо товар вже є в корзині, але валюта змінилась — перезапишемо ціну/валюту
        if self.cart[product_id].get("currency") != currency:
            self.cart[product_id]["currency"] = currency
            self.cart[product_id]["price"] = str(price)

        if override_qty:
            self.cart[product_id]["qty"] = qty
        else:
            self.cart[product_id]["qty"] += qty

        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = [int(pid) for pid in self.cart.keys()]
        products = Product.objects.filter(id__in=product_ids)

        existing_ids = set(str(p.id) for p in products)
        for pid in list(self.cart.keys()):
            if pid not in existing_ids:
                del self.cart[pid]
        if len(existing_ids) != len(product_ids):
            self.save()

        cart = self.cart.copy()
        for p in products:
            cart[str(p.id)]["product"] = p

        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["qty"]
            yield item

    def update_prices(self):
        product_ids = [int(pid) for pid in self.cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        currency = self._get_currency()

        for product in products:
            product_id = str(product.id)
            new_price = self._get_price_for_product(product, currency)
            self.cart[product_id]["price"] = str(new_price)
            self.cart[product_id]["currency"] = currency

        self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session.pop(settings.CART_SESSION_ID, None)
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for p in products:
            cart[str(p.id)]["product"] = p

        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["qty"]
            yield item

    def __len__(self):
        return sum(item["qty"] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item["price"]) * item["qty"] for item in self.cart.values())

    def get_currency(self):
        # валюта “корзини” — беремо з першого елемента або з сесії
        for item in self.cart.values():
            return item.get("currency", self._get_currency())
        return self._get_currency()

    def get_currency_symbol(self):
        currency = self.get_currency()
        symbols = {
            "UAH": "₴",
            "USD": "$",
            "EUR": "€",
        }
        return symbols.get(currency, currency)

    def is_empty(self):
        return len(self.cart) == 0

    def get_product_ids(self):
        return list(self.cart.keys())
