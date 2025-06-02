# purchase/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.purchase_dashboard, name='purchase_dashboard'),
    
    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    
    # Purchase Order URLs
    path('orders/', views.purchase_order_list, name='purchase_order_list'),
    path('orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('orders/<int:pk>/edit/', views.purchase_order_update, name='purchase_order_update'),
    path('orders/<int:pk>/confirm/', views.purchase_order_confirm, name='purchase_order_confirm'),
    path('orders/<int:pk>/receive/', views.purchase_order_receive, name='purchase_order_receive'),
    path('orders/<int:pk>/cancel/', views.purchase_order_cancel, name='purchase_order_cancel'),
    path('orders/<int:pk>/print/', views.purchase_order_print, name='purchase_order_print'),
    
    # AJAX URLs
    path('ajax/material/<int:material_id>/price/', views.get_material_purchase_price, name='get_material_purchase_price'),
]
