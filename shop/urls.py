from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.catalog_home, name="catalog_home"),
    path("currency/<str:code>/", views.set_currency, name="set_currency"),
    path("p/<slug:slug>/", views.product_detail, name="product_detail"),
    path("<slug:slug>/", views.category_detail, name="category_detail"),
]
