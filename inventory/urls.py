'''Datta outliar enhnaced code'''
# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Use item_list instead of material_list to match your template
    path('items/', views.material_list, name='item_list'),
    path('items/<int:pk>/', views.material_detail, name='material_detail'),
    # Add other URLs as needed
]
