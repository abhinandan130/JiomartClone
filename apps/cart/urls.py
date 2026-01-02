from django.urls import path
from . import views

urlpatterns = [
    # ================= CART PAGES =================
    path("cart/", views.cart_page, name="cart_page"),

    # ================= CART APIs =================
    path("api/cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("api/cart/count/", views.cart_count, name="cart_count"),
    path("api/cart/update/<int:item_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    path("api/cart/preview/", views.cart_preview, name="cart_preview"),

    # Optional Buy Now (not required if handled in JS)
    # path("api/cart/buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
]
