# purchase/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import transaction as db_transaction
from django.db.models import Sum, Count, Q
from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from .forms import SupplierForm, PurchaseOrderForm, PurchaseOrderItemFormSet
from inventory.models import BuildingMaterial
import datetime

@login_required
def purchase_dashboard(request):
    # Get current month data
    today = datetime.date.today()
    current_month_start = today.replace(day=1)
    
    # Statistics
    total_suppliers = Supplier.objects.count()
    monthly_purchases = PurchaseOrder.objects.filter(
        date__gte=current_month_start,
        status__in=['confirmed', 'received']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    pending_orders = PurchaseOrder.objects.filter(status='confirmed').count()
    recent_orders = PurchaseOrder.objects.exclude(status='cancelled').order_by('-created_at')[:5]
    
    # Low stock materials (less than 20% of average)
    low_stock_materials = BuildingMaterial.objects.filter(
        current_stock__lt=100  # You can adjust this threshold
    ).order_by('current_stock')[:5]
    
    context = {
        'total_suppliers': total_suppliers,
        'monthly_purchases': monthly_purchases,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
        'low_stock_materials': low_stock_materials,
    }
    return render(request, 'purchase/dashboard.html', context)


# Supplier Views
@login_required
def supplier_list(request):
    search_query = request.GET.get('search', '')
    
    suppliers = Supplier.objects.all()
    
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(gstin__icontains=search_query)
        )
    
    context = {
        'suppliers': suppliers,
        'search_query': search_query,
    }
    return render(request, 'purchase/supplier_list.html', context)


@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, 'Supplier created successfully!')
            
            # Check if this is from PO creation
            if request.GET.get('next') == 'po':
                return redirect('purchase_order_create')
            
            return redirect('supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm()
    
    return render(request, 'purchase/supplier_form.html', {
        'form': form,
        'title': 'Add New Supplier'
    })


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    orders = supplier.purchase_orders.exclude(status='cancelled').order_by('-date')[:10]
    
    # Calculate total business
    total_business = orders.filter(
        status='received'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'supplier': supplier,
        'orders': orders,
        'total_business': total_business,
    }
    return render(request, 'purchase/supplier_detail.html', context)


@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully!')
            return redirect('supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'purchase/supplier_form.html', {
        'form': form,
        'supplier': supplier,
        'title': 'Edit Supplier'
    })


# Purchase Order Views
@login_required
def purchase_order_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    orders = PurchaseOrder.objects.all()
    
    if search_query:
        orders = orders.filter(
            Q(po_number__icontains=search_query) |
            Q(supplier__name__icontains=search_query) |
            Q(reference_number__icontains=search_query)
        )
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if date_from:
        orders = orders.filter(date__gte=date_from)
    
    if date_to:
        orders = orders.filter(date__lte=date_to)
    
    orders = orders.order_by('-date', '-created_at')
    
    context = {
        'orders': orders,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': PurchaseOrder.STATUS_CHOICES,
    }
    return render(request, 'purchase/purchase_order_list.html', context)


@login_required
@db_transaction.atomic
def purchase_order_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Save purchase order
            order = form.save()
            
            # Save items
            items = formset.save(commit=False)
            for item in items:
                item.purchase_order = order
                item.save()
            
            # Delete removed items
            for item in formset.deleted_objects:
                item.delete()
            
            # Calculate totals
            order.calculate_totals()
            
            messages.success(request, 'Purchase order created successfully!')
            return redirect('purchase_order_detail', pk=order.pk)
    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet()
    
    return render(request, 'purchase/purchase_order_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Purchase Order'
    })


@login_required
def purchase_order_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'purchase/purchase_order_detail.html', {'order': order})


@login_required
@db_transaction.atomic
def purchase_order_update(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    
    # Only draft orders can be edited
    if order.status != 'draft':
        messages.error(request, 'Only draft orders can be edited.')
        return redirect('purchase_order_detail', pk=order.pk)
    
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        formset = PurchaseOrderItemFormSet(request.POST, instance=order)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            order.calculate_totals()
            
            messages.success(request, 'Purchase order updated successfully!')
            return redirect('purchase_order_detail', pk=order.pk)
    else:
        form = PurchaseOrderForm(instance=order)
        formset = PurchaseOrderItemFormSet(instance=order)
    
    return render(request, 'purchase/purchase_order_form.html', {
        'form': form,
        'formset': formset,
        'order': order,
        'title': 'Edit Purchase Order'
    })


@login_required
def purchase_order_confirm(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if order.status != 'draft':
        messages.error(request, 'Only draft orders can be confirmed.')
        return redirect('purchase_order_detail', pk=order.pk)
    
    if request.method == 'POST':
        order.confirm_order()
        messages.success(request, 'Purchase order confirmed successfully!')
        return redirect('purchase_order_detail', pk=order.pk)
    
    return render(request, 'purchase/purchase_order_confirm.html', {'order': order})


@login_required
@db_transaction.atomic
def purchase_order_receive(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if order.status != 'confirmed':
        messages.error(request, 'Only confirmed orders can be marked as received.')
        return redirect('purchase_order_detail', pk=order.pk)
    
    if request.method == 'POST':
        order.receive_order()
        messages.success(request, 'Purchase order received and inventory updated successfully!')
        return redirect('purchase_order_detail', pk=order.pk)
    
    return render(request, 'purchase/purchase_order_receive.html', {'order': order})


@login_required
def purchase_order_cancel(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if order.status not in ['draft', 'confirmed']:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('purchase_order_detail', pk=order.pk)
    
    if request.method == 'POST':
        order.cancel_order()
        messages.success(request, 'Purchase order cancelled successfully!')
        return redirect('purchase_order_list')
    
    return render(request, 'purchase/purchase_order_cancel.html', {'order': order})


@login_required
def purchase_order_print(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'purchase/purchase_order_print.html', {'order': order})


# AJAX Views
@login_required
def get_material_purchase_price(request, material_id):
    """AJAX view to get material purchase price"""
    try:
        material = BuildingMaterial.objects.get(pk=material_id)
        data = {
            'success': True,
            'unit': material.unit,
            'purchase_price': str(material.purchase_price),
            'current_stock': str(material.current_stock)
        }
    except BuildingMaterial.DoesNotExist:
        data = {'success': False}
    
    return JsonResponse(data)
