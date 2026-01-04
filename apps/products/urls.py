from django.urls import path
from .views import product_list, product_list_api, search_suggestions

urlpatterns = [
    path("", product_list, name="product_list"),
    path("api/products/", product_list_api, name="product_list_api"),
    path("api/search/suggestions/", search_suggestions, name="search_suggestions"),
]
