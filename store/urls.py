from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home_url"),
    path('brand/<int:brand_id>/', views.home, name="brand_filter_url"), # <-- NEW URL for filtering
    path('phone/<int:phone_id>/', views.phone_detail, name="phone_detail_url"),
    path('dashboard/', views.custom_admin_dashboard, name="custom_admin_dashboard_url"),
    path('dashboard/edit/<int:phone_id>/', views.edit_phone, name="edit_phone_url"),
    path('dashboard/delete/<int:phone_id>/', views.delete_phone, name="delete_phone_url"),
    path('cart/', views.view_cart, name="cart_view_url"),
    path('cart/add/<int:phone_id>/', views.add_to_cart, name="add_to_cart_url"),
    path('cart/', views.view_cart, name="cart_view_url"),
    path('cart/add/<int:phone_id>/', views.add_to_cart, name="add_to_cart_url"),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name="remove_from_cart_url"),
]