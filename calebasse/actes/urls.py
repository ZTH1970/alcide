from django.conf.urls import patterns, url
from calebasse.cbv import ListView, CreateView, DeleteView, UpdateView

from models import Act
from forms import CreateActForm, EditActForm

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Act)),
    url(r'^nouveau/$', CreateView.as_view(model=Act,
        form_class=CreateActForm,
        template_name_suffix='_nouveau.html')),
    url(r'^(?P<pk>\d+)/$', UpdateView.as_view(model=Act,
        form_class=EditActForm,
        template_name_suffix='_edit.html')),
    url(r'^(?P<pk>\d+)/supprimer/$', DeleteView.as_view(model=Act)),
)
