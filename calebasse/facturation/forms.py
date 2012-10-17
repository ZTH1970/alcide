from django.forms import ModelForm

from models import Invoice

class CreateInvoiceForm(ModelForm):
    class Meta:
        model = Invoice


class EditInvoiceForm(ModelForm):
    class Meta:
        model = Invoice
