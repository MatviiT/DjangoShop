from .models import Category


def nav_categories(request):
    return {"nav_categories": Category.objects.all().order_by("name")}
