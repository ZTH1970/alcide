from django import forms
from django.forms import ModelForm, Form

from models import Invoice

class CreateInvoiceForm(ModelForm):
    class Meta:
        model = Invoice


class EditInvoiceForm(ModelForm):
    class Meta:
        model = Invoice

class CloseInvoicingForm(Form):
    invoicing_id = forms.IntegerField()
    service_name = forms.CharField()
    date = forms.DateField(label=u'Date', localize=True)

class FacturationRebillForm(Form):
    invoice_id = forms.IntegerField()
