from django.db import models
from django.http import Http404
from django.shortcuts import render

from calebasse.cbv import ListView, CreateView, UpdateView, DeleteView


_models = None


def get_ressource_model(model_name):
    global _models
    if _models is None:
        _models = models.get_models()
    for model in _models:
        meta = model._meta
        if meta.module_name == model_name and meta.app_label == 'ressources':
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
    return render(request, 'ressources/index.html',
            dict(models=sorted(ressources_models)))


def list_view(request, service, model_name):
    model = get_ressource_model(model_name)
    if model is None:
        raise Http404
    view = ListView.as_view(model=model, template_name='ressources/list.html')
    return view(request, service=service)


def create_view(request, service, model_name):
    model = get_ressource_model(model_name)
    if model is None:
        raise Http404
    view = CreateView.as_view(model=model,
            success_url='../',
            template_name="ressources/new.html",
            template_name_suffix='_new')
    return view(request, service=service)


def update_view(request, service, model_name, pk):
    model = get_ressource_model(model_name)
    if model is None:
        raise Http404
    view = UpdateView.as_view(model=model,
            success_url='../',
            template_name='ressources/update.html',
            template_name_suffix='_update')
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
