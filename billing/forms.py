from django import forms
from .models import Invoice, InvoiceItem, Product
from sales.models import Customer

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'customer', 'invoice_number', 'date', 'due_date',
            'additional_cost', 'discount'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally limit customer queryset if needed
        self.fields['customer'].queryset = Customer.objects.all()
        

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'rate', 'gst_rate']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Automatically fill rate and gst_rate based on selected product (JS on frontend)
        self.fields['rate'].required = False
        self.fields['gst_rate'].required = False

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        if product:
            if not cleaned_data.get('rate'):
                cleaned_data['rate'] = product.price
            if not cleaned_data.get('gst_rate'):
                cleaned_data['gst_rate'] = product.gst_rate
        return cleaned_data
