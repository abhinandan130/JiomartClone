from django.shortcuts import render
from django.http import JsonResponse
from .models import Product

def product_list(request):
    query = request.GET.get("q", "").strip()

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    return render(request, "products/product_list.html", {
        "products": products,
        "search_query": query,
    })

def product_list_api(request):
    """
    Returns products as JSON for JS.
    """
    products = Product.objects.filter(is_active=True)

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": str(p.price),
            "category": p.category,
            "image": p.image.url if p.image else "",
        })

    return JsonResponse({"products": data})


def search_suggestions(request):
    q = request.GET.get("q", "").strip()

    if not q or len(q) < 2:
        return JsonResponse({"results": []})

    products = (
        Product.objects
        .filter(name__icontains=q, is_active=True)
        .values("id", "name")[:8]
    )

    return JsonResponse({"results": list(products)})