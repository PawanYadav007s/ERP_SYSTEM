<<<<<<< HEAD
from django.db import models
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=100)   
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
=======
# sales/models.py
from django.db import models
from django.core.validators import RegexValidator
from inventory.models import BuildingMaterial, StockTransaction
from decimal import Decimal
from django.db import transaction
import datetime

class Customer(models.Model):
    """Customer model for managing customer information"""
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
    address_site = models.TextField(help_text='Site/Delivery Address')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
>>>>>>> e3e9bf4 (all working code added remaining inventory and admin panel app userinterface else other functionalities works properly)

    def __str__(self):
        return self.name

<<<<<<< HEAD

class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=4, decimal_places=2, default=18.0)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales_invoices')
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=4, decimal_places=2)

    def line_total(self):
        return self.unit_price * self.quantity

    def gst_amount(self):
        return self.line_total() * (self.gst_rate / 100)

    def total_with_gst(self):
        return self.line_total() + self.gst_amount()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Payment of {self.amount} on {self.payment_date}"
=======
    class Meta:
        ordering = ['name']


class Invoice(models.Model):
    """Invoice model for sales transactions"""
    bill_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices')
    date = models.DateField(default=datetime.date.today)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # GST Rate (default 5% split into CGST and SGST)
    gst_rate = models.DecimalField(max_digits=4, decimal_places=2, default=5.0)
    
    # Additional fields
    authorized_signatory = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)

    def __str__(self):
        return f"Invoice #{self.bill_number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        if not self.bill_number:
            # Generate bill number starting from 254
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice and last_invoice.bill_number.isdigit():
                new_number = int(last_invoice.bill_number) + 1
            else:
                new_number = 254
            self.bill_number = str(new_number)
        
        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculate invoice totals from line items"""
        self.subtotal = sum(item.amount for item in self.items.all())
        
        # Calculate GST (CGST + SGST)
        gst_amount = self.subtotal * (self.gst_rate / 100)
        self.cgst_amount = gst_amount / 2
        self.sgst_amount = gst_amount / 2
        
        self.total_amount = self.subtotal + gst_amount
        self.save()

    def get_amount_in_words(self):
        """Convert total amount to words"""
        try:
            from num2words import num2words
            return num2words(int(self.total_amount), lang='en_IN').title() + " Only"
        except:
            return ""

    class Meta:
        ordering = ['-date', '-created_at']


class InvoiceItem(models.Model):
    """Line items for each invoice"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    date = models.DateField()
    challan_number = models.CharField(max_length=50, blank=True)
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
        ordering = ['date', 'id']
        
>>>>>>> e3e9bf4 (all working code added remaining inventory and admin panel app userinterface else other functionalities works properly)
