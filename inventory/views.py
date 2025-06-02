'''Pawan initial code
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Item

@login_required
def item_list(request):
    items = Item.objects.all()
    return render(request, 'inventory/item_list.html', {'items': items})
'''

'''Datta outliar enhnaced code'''
# inventory/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import BuildingMaterial

# Define your view functions here
def material_list(request):
    materials = BuildingMaterial.objects.all().order_by('name')
    return render(request, 'inventory/material_list.html', {'materials': materials})

def material_detail(request, pk):
    material = get_object_or_404(BuildingMaterial, pk=pk)
    return render(request, 'inventory/material_detail.html', {'material': material})

def material_create(request):
    # Implementation for creating materials
    pass

def material_update(request, pk):
    # Implementation for updating materials
    pass

def stock_transaction_list(request):
    # Implementation for listing stock transactions
    pass
