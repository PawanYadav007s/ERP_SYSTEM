'''Pawan initial code
from django.contrib import admin
from .models import Item
from .models import StockTransaction

admin.site.register(Item)
admin.site.register(StockTransaction)
'''
'''Datta outliar enhnaced code'''
# inventory/admin.py
from django.contrib import admin
from .models import BuildingMaterial, StockTransaction

# Register your models
admin.site.register(BuildingMaterial)
admin.site.register(StockTransaction)
