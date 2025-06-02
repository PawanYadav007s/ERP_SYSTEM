# purchase/admin.py
from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'gstin', 'created_at']
    search_fields = ['name', 'phone', 'gstin']
    list_filter = ['created_at']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'date', 'total_amount', 'status']
    list_filter = ['status', 'date']
    search_fields = ['po_number', 'supplier__name', 'reference_number']
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ['subtotal', 'cgst_amount', 'sgst_amount', 'total_amount']
    