from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from apps.cart.models import Cart, CartItem
from apps.products.models import Product
from apps.accounts.decorators import nocache
from apps.orders.models import Address
import json


# =====================================
# ADD TO CART
# =====================================
@nocache
@require_POST
def add_to_cart(request, product_id):
    customer_id = request.session.get("user_id")
    if not customer_id:
        return JsonResponse({"error": "Login required"}, status=401)

    cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(cart=cart,product=product)

    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1

    cart_item.save()
    return JsonResponse({"success": True})


# =====================================
# CART COUNT (NAVBAR)
# =====================================
@nocache
def cart_count(request):
    customer_id = request.session.get("user_id")
    if not customer_id:
        return JsonResponse({"count": 0})

    cart = Cart.objects.filter(customer_id=customer_id).first()
    if not cart:
        return JsonResponse({"count": 0})

    count = sum(item.quantity for item in cart.items.all())
    return JsonResponse({"count": count})


# =====================================
# CART PAGE
# =====================================
@nocache
def cart_page(request):
    customer_id = request.session.get("user_id")

    if not customer_id:
        return render(request, "cart/cart.html", {
            "items": [],
            "total": 0,
            "addresses": [],
            "hide_footer": True,
            "hide_navitems": True
        })

    cart = Cart.objects.filter(customer_id=customer_id).first()
    addresses = Address.objects.filter(customer_id=customer_id)

    items = []
    total = 0

    if cart:
        for item in cart.items.select_related("product"):
            subtotal = item.quantity * item.product.price
            total += subtotal

            items.append({
                "id": item.id,
                "name": item.product.name,
                "price": item.product.price,
                "quantity": item.quantity,
                "subtotal": subtotal,
                "image": item.product.image.url if item.product.image else ""
            })

    return render(request, "cart/cart.html", {
        "items": items,
        "total": total,
        "addresses": addresses,
        "hide_footer": True,
        "hide_navitems": True
    })


# =====================================
# UPDATE QUANTITY (+ / -)
# =====================================
@nocache
@require_POST
def update_cart_quantity(request, item_id):
    customer_id = request.session.get("user_id")
    if not customer_id:
        return JsonResponse({"error": "Login required"}, status=401)

    data = json.loads(request.body)
    action = data.get("action")

    cart_item = get_object_or_404(CartItem,id=item_id,cart__customer_id=customer_id)

    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease":
        cart_item.quantity -= 1

    if cart_item.quantity <= 0:
        cart_item.delete()
        quantity = 0
        subtotal = 0
    else:
        cart_item.save()
        quantity = cart_item.quantity
        subtotal = cart_item.quantity * cart_item.product.price

    cart_items = CartItem.objects.filter(cart__customer_id=customer_id)
    cart_total = sum(
        item.quantity * item.product.price for item in cart_items
    )

    return JsonResponse({
        "quantity": quantity,
        "subtotal": subtotal,
        "cart_total": cart_total
    })


# =====================================
# CART PREVIEW (HOVER)
# =====================================
def cart_preview(request):
    customer_id = request.session.get("user_id")

    if not customer_id:
        return JsonResponse({"logged_in": False})

    cart = Cart.objects.filter(customer_id=customer_id).first()
    if not cart:
        return JsonResponse({"logged_in": True, "items": [], "total": 0})

    items_qs = CartItem.objects.filter(cart=cart).select_related("product")
    if not items_qs.exists():
        return JsonResponse({"logged_in": True, "items": [], "total": 0})

    items = []
    total = 0

    for item in items_qs:
        subtotal = item.product.price * item.quantity
        total += subtotal

        items.append({
            "name": item.product.name,
            "quantity": item.quantity,
            "subtotal": float(subtotal),
            "image": item.product.image.url if item.product.image else ""
        })

    return JsonResponse({
        "logged_in": True,
        "items": items,
        "total": float(total)
    })