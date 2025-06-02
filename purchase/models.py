# purchase/models.py
from django.db import models
from django.core.validators import RegexValidator
from inventory.models import BuildingMaterial, StockTransaction
from decimal import Decimal
from django.db import transaction
import datetime

class Supplier(models.Model):
    """Supplier model for managing supplier information"""
    name = models.CharField(max_length=200)
    gstin = models.CharField(
        max_length=15, 
        blank=True,
        validators=[RegexValidator(
            regex='^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
            message='Enter a valid GSTIN'
        )],
        help_text='15-character GSTIN'
    )
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    bank_ifsc = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class PurchaseOrder(models.Model):
    """Purchase Order model for stock purchases"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    po_number = models.CharField(max_length=20, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    date = models.DateField(default=datetime.date.today)
    delivery_date = models.DateField(null=True, blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # GST Rate
    gst_rate = models.DecimalField(max_digits=4, decimal_places=2, default=5.0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Additional fields
    reference_number = models.CharField(max_length=50, blank=True, help_text='Supplier bill/invoice number')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO #{self.po_number} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        if not self.po_number:
            # Generate PO number: PO-YYYYMM-XXX format
            today = datetime.date.today()
            prefix = f"PO-{today.strftime('%Y%m')}"
            
            # Get the last PO of current month
            last_po = PurchaseOrder.objects.filter(
                po_number__startswith=prefix
            ).order_by('po_number').last()
            
            if last_po:
                last_number = int(last_po.po_number.split('-')[2])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.po_number = f"{prefix}-{new_number:03d}"
        
        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculate purchase order totals from line items"""
        self.subtotal = sum(item.amount for item in self.items.all())
        
        # Calculate GST
        gst_amount = self.subtotal * (self.gst_rate / 100)
        self.cgst_amount = gst_amount / 2
        self.sgst_amount = gst_amount / 2
        
        self.total_amount = self.subtotal + gst_amount
        self.save()

    def confirm_order(self):
        """Confirm the purchase order"""
        if self.status == 'draft':
            self.status = 'confirmed'
            self.save()

    def receive_order(self):
        """Mark order as received and update inventory"""
        if self.status == 'confirmed':
            with transaction.atomic():
                # Create stock transactions for each item
                for item in self.items.all():
                    # Debug print
                    print(f"Creating stock transaction for {item.material.name}, quantity: {item.quantity}")
                    
                    stock_transaction = StockTransaction.objects.create(
                        material=item.material,
                        transaction_type='IN',
                        quantity=item.quantity,
                        reference=f"PO-{self.po_number}",
                        note=f"Purchase from {self.supplier.name}"
                    )
                    
                    # Force refresh the material to get updated stock
                    item.material.refresh_from_db()
                    print(f"New stock for {item.material.name}: {item.material.current_stock}")
                
                self.status = 'received'
                self.save()

    def cancel_order(self):
        """Cancel the purchase order"""
        if self.status in ['draft', 'confirmed']:
            self.status = 'cancelled'
            self.save()

    class Meta:
        ordering = ['-date', '-created_at']


class PurchaseOrderItem(models.Model):
    """Line items for each purchase order"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey(BuildingMaterial, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculate amount
        self.amount = Decimal(str(self.quantity)) * Decimal(str(self.rate))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.material.name} - {self.quantity} {self.material.unit}"

    class Meta:
        ordering = ['id']
