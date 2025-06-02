# sales/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.sales_dashboard, name='sales_dashboard'),
    
    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    
    # Invoice URLs
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/print/', views.invoice_print, name='invoice_print'),
    path('invoices/<int:pk>/cancel/', views.invoice_cancel, name='invoice_cancel'),
    
    # AJAX URLs
    path('ajax/material/<int:material_id>/', views.get_material_details, name='get_material_details'),
]
