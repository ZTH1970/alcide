from django.conf.urls import patterns, url
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from models import Facturation
from forms import CreateFacturationForm, EditFacturationForm

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Facturation)),
    url(r'^nouveau/$', CreateView.as_view(model=Facturation,
        form_class=CreateFacturationForm,
        template_name_suffix='_nouveau.html')),
    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=Facturation,
        form_class=EditFacturationForm,
        template_name_suffix='_edit.html')),
    url(r'^(?P<pk>\d+)/supprimer/$', DeleteView.as_view(model=Facturation)),
)
