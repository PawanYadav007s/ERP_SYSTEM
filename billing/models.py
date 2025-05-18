from django.db import models
from django.utils import timezone
from sales.models import Customer  # Assuming your Customer model is here


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    hsn_code = models.CharField(max_length=20, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 18.00 for 18%

    def __str__(self):
        return self.name


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='billing_invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    additional_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cgst = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igst = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.invoice_number

    def calculate_totals(self):
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.cgst = sum(item.line_total * item.gst_rate / 200 for item in items)  # half GST as CGST
        self.sgst = self.cgst  # Assuming CGST = SGST
        self.igst = 0  # or calculate if interstate
        
        self.total = self.subtotal + self.cgst + self.sgst + self.igst + self.additional_cost - self.discount

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)  # Save invoice to get primary key
        self.calculate_totals()
        super().save(*args, **kwargs)  # Save again to update totals


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def calculate_line_total(self):
        self.line_total = self.quantity * self.rate

    def save(self, *args, **kwargs):
        if not self.rate:
            self.rate = self.product.price
        if not self.gst_rate:
            self.gst_rate = self.product.gst_rate
        self.calculate_line_total()
        super().save(*args, **kwargs)

        # After saving item, update invoice totals
        # To avoid infinite recursion, call update totals without saving invoice twice
        self.invoice.calculate_totals()
        Invoice.objects.filter(pk=self.invoice.pk).update(
            subtotal=self.invoice.subtotal,
            cgst=self.invoice.cgst,
            sgst=self.invoice.sgst,
            igst=self.invoice.igst,
            total=self.invoice.total,
        )
