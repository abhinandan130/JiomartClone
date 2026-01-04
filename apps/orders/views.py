from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from apps.accounts.decorators import nocache
from apps.cart.models import Cart
from .models import Order, OrderItem, Address
from .utils.invoice import generate_invoice_pdf


@nocache
@require_POST
@transaction.atomic
def create_order(request):
    customer_id = request.session.get("user_id")
    if not customer_id:
        messages.error(request, "Login required.")
        return redirect("login")

    address_id = request.POST.get("address_id")
    if not address_id:
        messages.error(request, "Select delivery address.")
        return redirect("cart_page")

    address = Address.objects.filter(id=address_id, customer_id=customer_id).first()
    if not address:
        messages.error(request, "Invalid address.")
        return redirect("cart_page")

    cart = Cart.objects.filter(customer_id=customer_id).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Cart is empty.")
        return redirect("cart_page")

    total_amount = Decimal("0.00")
    for item in cart.items.select_related("product"):
        if item.product.stock < item.quantity:
            messages.error(request, f"Insufficient stock for {item.product.name}")
            return redirect("cart_page")
        total_amount += item.quantity * item.product.price

    order = Order.objects.create(
        customer_id=customer_id,
        address=address,
        total_amount=total_amount,
        payment_status="pending",
        status="pending"
    )

    for item in cart.items.select_related("product"):
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
            subtotal=item.quantity * item.product.price
        )
        item.product.stock -= item.quantity
        item.product.save(update_fields=["stock"])

    return redirect("payment_options", order_number=order.order_number)


@nocache
def add_address(request):
    if not request.session.get("user_id"):
        return redirect("login")

    if request.method == "POST":
        Address.objects.create(
            customer_id=request.session["user_id"],
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            address_line=request.POST.get("address_line"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
        )
        return redirect("cart_page")

    return render(request, "orders/add_address.html")



@nocache
def payment_options(request, order_number):
    order = Order.objects.filter(order_number=order_number,customer_id=request.session.get("user_id")).first()
    if not order:
        return redirect("cart_page")
    return render(request, "orders/payment_options.html", {
        "order": order,
        "hide_navitems": True
    })


@require_POST
@transaction.atomic
def confirm_payment(request):
    customer_id = request.session.get("user_id")
    if not customer_id:
        return redirect("login")

    order_number = request.POST.get("order_number")
    payment_method = request.POST.get("payment_method")

    if not order_number or not payment_method:
        messages.error(request, "Invalid payment request.")
        return redirect("cart_page")

    order = Order.objects.filter(order_number=order_number,customer_id=customer_id,payment_status="pending").first()

    if not order:
        messages.error(request, "Order not found.")
        return redirect("cart_page")

    order.payment_method = payment_method
    order.payment_status = "success"
    order.status = "paid"
    order.save(update_fields=["payment_method", "payment_status", "status"])

    cart = Cart.objects.filter(customer_id=customer_id).first()
    if cart:
        cart.items.all().delete()

    return redirect("order_success", order_number=order.order_number)



@nocache
def order_success(request, order_number):
    order = Order.objects.filter(order_number=order_number,customer_id=request.session.get("user_id")).prefetch_related("items__product").first()
    if not order:
        return redirect("product_list")
    return render(request, "orders/order_success.html", {"order": order, "hide_navitems": True})


@nocache
def my_orders(request):
    if not request.session.get("user_id"):
        return redirect("login")
    orders = Order.objects.filter(customer_id=request.session["user_id"]).prefetch_related("items__product").order_by("-created_at")
    return render(request, "orders/my_orders.html", {
        "orders": orders,
        "hide_navitems": True
    })


@nocache
def order_detail(request, order_number):
    order = Order.objects.filter(order_number=order_number,customer_id=request.session.get("user_id")).prefetch_related("items__product").first()
    if not order:
        messages.error(request, "Order not found.")
        return redirect("my_orders")
    return render(request, "orders/order_detail.html", {
        "order": order,
        "hide_navitems": True
    })


@nocache
def download_invoice(request, order_number):
    if not request.session.get("user_id"):
        return HttpResponseForbidden("Login required")

    order = get_object_or_404(Order,order_number=order_number,customer_id=request.session["user_id"])
    return generate_invoice_pdf(order)
