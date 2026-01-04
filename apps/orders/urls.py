from django.urls import path
from .views import create_order, payment_options, confirm_payment, order_success, my_orders, order_detail, add_address, download_invoice

urlpatterns = [
    path("create/", create_order, name="create_order"),
    path("payment/<str:order_number>/", payment_options, name="payment_options"),
    path("confirm-payment/", confirm_payment, name="confirm_payment"),
    path("success/<str:order_number>/", order_success, name="order_success"),
    path("my-orders/", my_orders, name="my_orders"),
    path("order/<str:order_number>/", order_detail, name="order_detail"),
    path("add-address/", add_address, name="add_address"),
    path("invoice/<str:order_number>/", download_invoice, name="download_invoice"),
]