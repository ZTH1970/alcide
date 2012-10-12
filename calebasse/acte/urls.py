from django.conf.urls import patterns, url
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from models import Acte
from forms import CreateActeForm, EditActeForm

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Acte)),
    url(r'^nouveau/$', CreateView.as_view(model=Acte,
        form_class=CreateActeForm,
        template_name_suffix='_nouveau.html')),
    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=Acte,
        form_class=EditActeForm,
        template_name_suffix='_edit.html')),
    url(r'^(?P<pk>\d+)/supprimer/$', DeleteView.as_view(model=Acte)),
)
