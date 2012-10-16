from django.conf.urls import patterns, url

from calebasse.cbv import ListView, CreateView, DeleteView, UpdateView

from models import Facture
from forms import CreateFactureForm, EditFactureForm

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Facture)),
    url(r'^nouveau/$', CreateView.as_view(model=Facture,
        form_class=CreateFactureForm,
        template_name_suffix='_nouveau.html')),
    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=Facture,
        form_class=EditFactureForm,
        template_name_suffix='_edit.html')),
    url(r'^(?P<pk>\d+)/supprimer/$', DeleteView.as_view(model=Facture)),
)
