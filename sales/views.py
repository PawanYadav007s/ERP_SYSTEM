<<<<<<< HEAD
from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer
from .forms import CustomerForm

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'sales/customer_list.html', {'customers': customers})

=======
# sales/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import transaction as db_transaction
from django.template.loader import render_to_string
from django.db.models import Sum, Count, Q
from .models import Customer, Invoice, InvoiceItem
from .forms import CustomerForm, InvoiceForm, InvoiceItemFormSet
from inventory.models import BuildingMaterial, StockTransaction
import datetime
from decimal import Decimal

@login_required
def sales_dashboard(request):
    # Get current month data
    today = datetime.date.today()
    current_month_start = today.replace(day=1)
    
    # Statistics
    total_customers = Customer.objects.count()
    monthly_sales = Invoice.objects.filter(
        date__gte=current_month_start,
        is_cancelled=False
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    pending_invoices = Invoice.objects.filter(is_cancelled=False).count()
    recent_invoices = Invoice.objects.filter(is_cancelled=False).order_by('-created_at')[:5]
    
    # Top selling materials
    top_materials = InvoiceItem.objects.filter(
        invoice__is_cancelled=False,
        invoice__date__gte=current_month_start
    ).values('material__name').annotate(
        total_qty=Sum('quantity'),
        total_amount=Sum('amount')
    ).order_by('-total_amount')[:5]
    
    context = {
        'total_customers': total_customers,
        'monthly_sales': monthly_sales,
        'pending_invoices': pending_invoices,
        'recent_invoices': recent_invoices,
        'top_materials': top_materials,
    }
    return render(request, 'sales/dashboard.html', context)

# Customer Views
@login_required
def customer_list(request):
    search_query = request.GET.get('search', '')
    
    customers = Customer.objects.all()
    
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(gstin__icontains=search_query)
        )
    
    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'sales/customer_list.html', context)


@login_required
>>>>>>> e3e9bf4 (all working code added remaining inventory and admin panel app userinterface else other functionalities works properly)
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
<<<<<<< HEAD
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'sales/customer_form.html', {'form': form})

def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
=======
            customer = form.save()
            messages.success(request, 'Customer created successfully!')
            
            # Check if this is from invoice creation
            if request.GET.get('next') == 'invoice':
                return redirect('invoice_create')
            
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    
    return render(request, 'sales/customer_form.html', {
        'form': form,
        'title': 'Add New Customer'
    })


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    invoices = customer.invoices.filter(is_cancelled=False).order_by('-date')[:10]
    
    # Calculate total business
    total_business = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'customer': customer,
        'invoices': invoices,
        'total_business': total_business,
    }
    return render(request, 'sales/customer_detail.html', context)


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
>>>>>>> e3e9bf4 (all working code added remaining inventory and admin panel app userinterface else other functionalities works properly)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
<<<<<<< HEAD
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'sales/customer_form.html', {'form': form})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'sales/customer_confirm_delete.html', {'customer': customer})
=======
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'sales/customer_form.html', {
        'form': form,
        'customer': customer,
        'title': 'Edit Customer'
    })


# Invoice Views
@login_required
def invoice_list(request):
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    invoices = Invoice.objects.filter(is_cancelled=False)
    
    if search_query:
        invoices = invoices.filter(
            Q(bill_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )
    
    if date_from:
        invoices = invoices.filter(date__gte=date_from)
    
    if date_to:
        invoices = invoices.filter(date__lte=date_to)
    
    invoices = invoices.order_by('-date', '-created_at')
    
    context = {
        'invoices': invoices,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'sales/invoice_list.html', context)


@login_required
@db_transaction.atomic
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Save invoice
            invoice = form.save()
            
            # Save items
            items = formset.save(commit=False)
            for item in items:
                item.invoice = invoice
                item.save()
                
                # Create stock transaction
                StockTransaction.objects.create(
                    material=item.material,
                    transaction_type='OUT',
                    quantity=item.quantity,
                    reference=f"INV-{invoice.bill_number}",
                    note=f"Sale to {invoice.customer.name}"
                )
            
            # Delete removed items
            for item in formset.deleted_objects:
                item.delete()
            
            # Calculate totals
            invoice.calculate_totals()
            
            messages.success(request, 'Invoice created successfully!')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()
    
    return render(request, 'sales/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice'
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'sales/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_print(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'sales/invoice_print.html', {'invoice': invoice})


@login_required
def invoice_cancel(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('cancellation_reason', '')
        
        with db_transaction.atomic():
            # Reverse stock transactions
            for item in invoice.items.all():
                StockTransaction.objects.create(
                    material=item.material,
                    transaction_type='IN',
                    quantity=item.quantity,
                    reference=f"CANCELLED-INV-{invoice.bill_number}",
                    note=f"Cancelled invoice - {reason}"
                )
            
            # Mark invoice as cancelled
            invoice.is_cancelled = True
            invoice.cancellation_reason = reason
            invoice.save()
        
        messages.success(request, 'Invoice cancelled successfully!')
        return redirect('invoice_list')
    
    return render(request, 'sales/invoice_cancel.html', {'invoice': invoice})


# AJAX Views
@login_required
def get_material_details(request, material_id):
    """AJAX view to get material details"""
    try:
        material = BuildingMaterial.objects.get(pk=material_id)
        data = {
            'success': True,
            'unit': material.unit,
            'selling_price': str(material.selling_price),
            'current_stock': str(material.current_stock)
        }
    except BuildingMaterial.DoesNotExist:
        data = {'success': False}
    
    return JsonResponse(data)
>>>>>>> e3e9bf4 (all working code added remaining inventory and admin panel app userinterface else other functionalities works properly)
