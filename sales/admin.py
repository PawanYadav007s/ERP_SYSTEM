<<<<<<< HEAD
from django.contrib import admin
from .models import Customer, Product, Invoice, InvoiceItem, Payment

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Payment)
=======
# sales/admin.py
from django.contrib import admin
from .models import Customer, Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'gstin', 'created_at']
    search_fields = ['name', 'phone', 'gstin']
    list_filter = ['created_at']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'customer', 'date', 'total_amount', 'is_cancelled']
    list_filter = ['date', 'is_cancelled']
    search_fields = ['bill_number', 'customer__name']
    inlines = [InvoiceItemInline]
    readonly_fields = ['subtotal', 'cgst_amount', 'sgst_amount', 'total_amount']
    
>>>>>>> e3e9bf4 (all working code added remaining inventory and admin panel app userinterface else other functionalities works properly)
