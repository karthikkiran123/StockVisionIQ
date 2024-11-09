from django.urls import path
from .views import dashboard, login_staff, logout_user, orders, complete_order, users, invite_user, admin_delete_user, products, admin_delete_product, add_product, register_vendor

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('orders', orders, name='orders'),
    path('login', login_staff, name='admin_login'),
    path('logout', logout_user, name='admin_logout'),
    path('complete_order/<int:id>', complete_order, name='admin_complete_order'),
    path('users', users, name='admin_users'),
    path('invite', invite_user, name="admin_invite"),
    path('delete_user/<int:id>', admin_delete_user, name="admin_delete_user"),
    path('products/<str:type>', products, name='admin_products'),
    path('delete_product/<int:id>', admin_delete_product, name="admin_delete_product"),
    path('add_product', add_product, name="admin_add_product"),
    path('register_vendor', register_vendor, name="register_vendor")
]