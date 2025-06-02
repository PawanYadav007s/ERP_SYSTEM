# purchase/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from inventory.models import BuildingMaterial
import datetime

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'gstin', 'phone', 'email', 'address', 
                 'bank_name', 'bank_account', 'bank_ifsc']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Supplier Name'}),
            'gstin': forms.TextInput(attrs={'placeholder': 'GSTIN (optional)'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email (optional)'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Address'}),
            'bank_name': forms.TextInput(attrs={'placeholder': 'Bank Name (optional)'}),
            'bank_account': forms.TextInput(attrs={'placeholder': 'Account Number (optional)'}),
            'bank_ifsc': forms.TextInput(attrs={'placeholder': 'IFSC Code (optional)'}),
        }


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'date', 'delivery_date', 'gst_rate', 
                 'reference_number', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'gst_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'reference_number': forms.TextInput(attrs={'placeholder': 'Supplier Bill/Invoice Number'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Additional notes (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = datetime.date.today()


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['material', 'quantity', 'rate']
        widgets = {
            'material': forms.Select(attrs={'class': 'material-select'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'class': 'quantity-input'}),
            'rate': forms.NumberInput(attrs={'step': '0.01', 'class': 'rate-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add material info to dropdown
        materials = BuildingMaterial.objects.all()
        self.fields['material'].queryset = materials
        choices = [(m.id, f"{m.name} (Current Stock: {m.current_stock} {m.unit})") for m in materials]
        choices.insert(0, ('', '---------'))
        self.fields['material'].choices = choices


# Formset for purchase order items
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder, 
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
