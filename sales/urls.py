<<<<<<< HEAD
=======
# sales/urls.py
>>>>>>> e3e9bf4 (all working code added remaining inventory and admin panel app userinterface else other functionalities works properly)
from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
=======
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
>>>>>>> e3e9bf4 (all working code added remaining inventory and admin panel app userinterface else other functionalities works properly)
]
