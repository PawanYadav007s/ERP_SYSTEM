# billing/views.py

from django.views import View
from django.views.generic import DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.urls import reverse
from .models import Invoice, InvoiceItem
from .forms import InvoiceForm, InvoiceItemForm
from django.http import HttpResponse
from django.template.loader import render_to_string
import io
from xhtml2pdf import pisa

class InvoiceListView(View):
    def get(self, request):
        invoices = Invoice.objects.all().order_by('-date')
        return render(request, 'billing/invoice_list.html', {'invoices': invoices})

class InvoiceCreateView(View):
    def get(self, request):
        InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True)
        form = InvoiceForm()
        formset = InvoiceItemFormSet()
        return render(request, 'billing/invoice_form.html', {'form': form, 'formset': formset})
    
    def post(self, request):
        InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True)
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.subtotal = 0
            invoice.cgst = 0
            invoice.sgst = 0
            invoice.total = 0
            invoice.save()

            total_amount = 0
            items = formset.save(commit=False)
            for item in items:
                item.invoice = invoice
                item.line_total = item.quantity * item.rate
                total_amount += item.line_total
                item.save()

            invoice.subtotal = total_amount
            invoice.cgst = total_amount * 0.09  # example CGST 9%
            invoice.sgst = total_amount * 0.09  # example SGST 9%
            invoice.total = total_amount + invoice.cgst + invoice.sgst
            invoice.save()

            return redirect(reverse('billing:invoice_list'))
        return render(request, 'billing/invoice_form.html', {'form': form, 'formset': formset})

class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'billing/invoice_detail.html'
    context_object_name = 'invoice'

class InvoicePDFView(View):
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)

        def number_to_words(amount):
            try:
                from num2words import num2words
                return num2words(amount, to='currency', lang='en_IN')
            except ImportError:
                return str(amount)

        context = {
            'bill': invoice,
            'amount_in_words': number_to_words(invoice.total),
        }
        html_string = render_to_string('billing/bill_pdf.html', context)
        result = io.BytesIO()

        pdf = pisa.CreatePDF(io.BytesIO(html_string.encode('UTF-8')), dest=result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'filename=invoice_{invoice.invoice_number}.pdf'
            return response
        else:
            return HttpResponse('Error generating PDF', status=400)
