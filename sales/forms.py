# sales/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Customer, Invoice, InvoiceItem
from inventory.models import BuildingMaterial
import datetime

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'gstin', 'phone', 'email', 'address_site']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Customer Name'}),
            'gstin': forms.TextInput(attrs={'placeholder': 'GSTIN (optional)'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email (optional)'}),
            'address_site': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Site/Delivery Address'}),
        }


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'date', 'gst_rate', 'authorized_signatory']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'gst_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'authorized_signatory': forms.TextInput(attrs={'placeholder': 'Authorized Signatory'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.date.today()


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['date', 'challan_number', 'material', 'quantity', 'rate']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'item-date'}),
            'challan_number': forms.TextInput(attrs={'placeholder': 'Challan No.'}),
            'material': forms.Select(attrs={'class': 'material-select'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'class': 'quantity-input'}),
            'rate': forms.NumberInput(attrs={'step': '0.01', 'class': 'rate-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.date.today()
        
        # Add material info to dropdown
        materials = BuildingMaterial.objects.all()
        self.fields['material'].queryset = materials
        choices = [(m.id, f"{m.name} (Stock: {m.current_stock} {m.unit})") for m in materials]
        choices.insert(0, ('', '---------'))
        self.fields['material'].choices = choices


# Formset for invoice items
InvoiceItemFormSet = inlineformset_factory(
    Invoice, 
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
