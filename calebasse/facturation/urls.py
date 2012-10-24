from django.conf.urls import patterns, url

from calebasse.cbv import ListView, CreateView, DeleteView, UpdateView

from models import Invoice
from forms import CreateInvoiceForm, EditInvoiceForm

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Invoice)),
    url(r'^new/$', CreateView.as_view(model=Invoice,
        form_class=CreateInvoiceForm,
        template_name_suffix='_new.html')),
    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=Invoice,
        form_class=EditInvoiceForm,
        template_name_suffix='_edit.html')),
    url(r'^(?P<pk>\d+)/supprimer/$', DeleteView.as_view(model=Invoice)),
)
