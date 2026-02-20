from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    # Homepage
    path("", views.home, name="home"),
    # Authentication URLs
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path(
        "password-reset/", views.password_reset_request, name="password_reset_request"
    ),
    path(
        "password-reset/<str:token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    # Dashboards
    path("vendor/dashboard/", views.vendor_dashboard, name="vendor_dashboard"),
    path("buyer/dashboard/", views.buyer_dashboard, name="buyer_dashboard"),
    # Vendor Store Management
    path("vendor/stores/", views.vendor_stores_list, name="vendor_stores_list"),
    path(
        "vendor/stores/create/", views.vendor_store_create, name="vendor_store_create"
    ),
    path(
        "vendor/stores/<int:pk>/", views.vendor_store_detail, name="vendor_store_detail"
    ),
    path(
        "vendor/stores/<int:pk>/edit/",
        views.vendor_store_edit,
        name="vendor_store_edit",
    ),
    path(
        "vendor/stores/<int:pk>/delete/",
        views.vendor_store_delete,
        name="vendor_store_delete",
    ),
    # Vendor Product Management
    path("vendor/products", views.vendor_products_list, name="vendor_products_list"),
    path(
        "vendor/stores/<int:store_pk>/products/add/",
        views.vendor_product_add,
        name="vendor_product_add",
    ),
    path(
        "vendor/products/<int:pk>/edit/",
        views.vendor_product_edit,
        name="vendor_product_edit",
    ),
    path(
        "vendor/products/<int:pk>/delete/",
        views.vendor_product_delete,
        name="vendor_product_delete",
    ),
    # Buyer Shopping
    # Browse all products
    path("products/", views.products_browse, name="products_browse"),
    # Product detail
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    # Buyer cart
    # View cart
    path("cart/", views.cart_view, name="cart_view"),
    # Add to cart
    path("cart/add/<int:product_pk>/", views.cart_add, name="cart_add"),
    # Update quantity
    path("cart/update/<int:product_pk>/", views.cart_update, name="cart_update"),
    # Remove from cart
    path("cart/remove/<int:product_pk>/", views.cart_remove, name="cart_remove"),
    # Clear entire cart
    path("cart/clear/", views.cart_clear, name="cart_clear"),
    # Buyer checkout and orders
    # Checkout page
    path("checkout/", views.checkout, name="checkout"),
    # Order history
    path("orders/", views.order_history, name="order_history"),
    # Order detail
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    # Reviews
    path("products/<int:product_pk>/review/", views.review_add, name="review_add"),
    # urls
    path("test-urls/", views.test_urls, name="test_urls"),
]
