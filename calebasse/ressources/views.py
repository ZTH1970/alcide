from django.db import models
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from calebasse.cbv import (ListView, CreateView, UpdateView, DeleteView,
        ReturnToObjectMixin)
from calebasse.ressources.models import Service


_models = None


def get_ressource_model(model_name):
    global _models
    if _models is None:
        _models = models.get_models()
    for model in _models:
        meta = model._meta
        if meta.module_name == model_name and \
                (meta.app_label == 'ressources' or meta.app_label == 'personnes'):
            return model
    return None


def homepage(request, service):
    global _models
    if _models is None:
        _models = models.get_models()
    ressources_models = [
            (model._meta.verbose_name_plural, model._meta.module_name)
            for model in _models
            if model._meta.app_label == 'ressources' ]
    service_name = get_object_or_404(Service, slug=service)
    return render(request, 'ressources/index.html',
            dict(models=sorted(ressources_models),
                service=service,
                service_name=service_name))


def list_view(request, service, model_name):
    model = get_ressource_model(model_name)
    if model is None:
        raise Http404
    view = ListView.as_view(model=model,
            queryset=model.objects.select_related(),
            template_name='ressources/list.html')
    return view(request, service=service)

class RessourceCreateView(CreateView):
    template_name="ressources/new.html"
    template_name_suffix='_new'

    def get_initial(self):
        initial = super(RessourceCreateView, self).get_initial()
        initial['service'] = self.service
        return initial

    def get_success_url(self):
        if self.request.GET.has_key('next_url'):
            return self.request.GET['next_url']
        else:
            return '../?new_id=%s' % self.object.id

def create_view(request, service, model_name):
    model = get_ressource_model(model_name)
    if model is None:
        raise Http404
    view = RessourceCreateView.as_view(model=model)
    return view(request, service=service)

class RessourceUpdateView(ReturnToObjectMixin, UpdateView):
    template_name='ressources/update.html'
    template_name_suffix='_update'

def update_view(request, service, model_name, pk):
    model = get_ressource_model(model_name)
    if model is None:
        raise Http404
    view = RessourceUpdateView.as_view(model=model)
    return view(request, pk=pk, service=service)


def delete_view(request, service, model_name, pk):
    model = get_ressource_model(model_name)
    if model is None:
        raise Http404
    view = DeleteView.as_view(model=model,
            success_url='../../',
            template_name='ressources/delete.html',
            template_name_suffix='_delete')
    return view(request, pk=pk, service=service)
