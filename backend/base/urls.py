from django.urls import path
from .views import (
    product_list,
    get_product_data,
    register_user,
    logout_user,
    profile_view,
    add_to_cart,
    update_cart_item,
    delete_cart_item,
    cart_view,
    create_xendit_payment,
    xendit_webhook,
    list_user_orders,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('products/', product_list, name="product_list"),
    path('products/<int:pk>/', get_product_data, name="product_data"),

    path('register/', register_user, name='register'),
    # login function
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile_view, name='profile'),

    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/update/<int:pk>/', update_cart_item, name='update_cart_item'),
    path('cart/delete/<int:pk>/', delete_cart_item, name='delete_cart_item'),
    path('cart/', cart_view, name='cart_view'),

    # Payment
    path('checkout/xendit/', create_xendit_payment, name='create_xendit_payment'),
    path('webhook/xendit/', xendit_webhook, name='xendit_webhook'),

    # Orders
    path('orders/', list_user_orders, name='orders'),


]
