from datetime import datetime
from dateutil.relativedelta import relativedelta

from django import forms
from django.views.generic import list as list_cbv, edit, base, detail
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import resolve
from django.core.exceptions import ImproperlyConfigured

from calebasse.ressources.models import Service

class ReturnToObjectMixin(object):
    def get_success_url(self):
        return '../#object-' + str(self.get_object().pk)

class ServiceFormMixin(object):
    def get_form_kwargs(self):
        kwargs = super(ServiceFormMixin, self).get_form_kwargs()
        kwargs['service'] = self.service
        return kwargs

class ServiceViewMixin(object):
    service = None
    date = None
    popup = False

    def dispatch(self, request, **kwargs):
        self.popup = request.GET.get('popup')
        if 'service' in kwargs:
            self.service = get_object_or_404(Service, slug=kwargs['service'])
        if 'date' in kwargs:
            try:
                self.date = datetime.strptime(kwargs.get('date'),
                        '%Y-%m-%d').date()
            except (TypeError, ValueError):
                raise Http404
        return super(ServiceViewMixin, self).dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ServiceViewMixin, self).get_context_data(**kwargs)
        context['url_name'] = resolve(self.request.path).url_name
        context['popup'] = self.popup
        if self.service is not None:
            context['service'] = self.service.slug
            context['service_name'] = self.service.name

        if self.date is not None:
            context['date'] = self.date
            context['previous_day'] = self.date + relativedelta(days=-1)
            context['next_day'] = self.date + relativedelta(days=1)
            context['previous_month'] = self.date + relativedelta(months=-1)
            context['next_month'] = self.date + relativedelta(months=1)
        return context

class TemplateView(ServiceViewMixin, base.TemplateView):
    pass

class ModelNameMixin(object):
    def get_context_data(self, **kwargs):
        ctx = super(ModelNameMixin, self).get_context_data(**kwargs)
        ctx['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        ctx['model_verbose_name'] = self.model._meta.verbose_name
        return ctx

class ListView(ModelNameMixin, ServiceViewMixin, list_cbv.ListView):
    pass


class CreateView(ModelNameMixin, ServiceViewMixin, edit.CreateView):
    pass


class DeleteView(ModelNameMixin, ServiceViewMixin, edit.DeleteView):
    pass


class UpdateView(ModelNameMixin, ServiceViewMixin, edit.UpdateView):
    pass

class FormView(ServiceViewMixin, edit.FormView):
    pass

class ContextMixin(object):
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data as the template context.
    """

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self
        return kwargs

class MultiFormMixin(ContextMixin):
    """
    A mixin that provides a way to show and handle multiple forms in a request.
    """

    initial = {}
    initials = {}
    forms_classes = None
    success_url = None

    def get_prefixes(self):
        return self.forms_classes.keys()

    def get_initial(self, prefix):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.initials.get(prefix, self.initial).copy()

    def get_form_class(self, prefix):
        """
        Returns the form class to use in this view
        """
        return self.forms_classes[prefix]

    def get_form(self, form_class, prefix):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(**self.get_form_kwargs(prefix))

    def get_current_prefix(self):
        """
        Returns the current prefix by parsing first keys in POST
        """
        keys = self.request.POST.keys() or self.request.FILES.keys()
        if not keys:
            return None
        return keys[0].split('-', 1)[0]

    def get_forms(self):
        """
        Returns the dictionnary of forms instances
        """
        form_instances = {}
        for prefix in self.get_prefixes():
            form_instances[prefix] = self.get_form(self.get_form_class(prefix), prefix)
        return form_instances

    def get_form_kwargs(self, prefix):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {'initial': self.get_initial(prefix),
                  'prefix': prefix }
        if self.request.method in ('POST', 'PUT') \
                and prefix == self.get_current_prefix():
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_success_url(self):
        """
        Returns the supplied success URL.
        """
        if self.success_url:
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def form_valid(self, forms):
        """
        If the form is valid, redirect to the supplied URL.
        """
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, forms):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(forms=forms))

class MultiModelFormMixin(MultiFormMixin, detail.SingleObjectMixin):
    """
    A mixin that provides a way to show and handle multiple forms or modelforms
    in a request.
    """

    def get_form_kwargs(self, prefix):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(MultiModelFormMixin, self).get_form_kwargs(prefix)
        if issubclass(self.get_form_class(prefix), forms.ModelForm):
            kwargs.update({'instance': self.object})
        return kwargs

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        if self.success_url:
            url = self.success_url % self.object.__dict__
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def form_valid(self, forms, commit=True):
        """
        If the form is valid, save the associated model.
        """
        form = forms[self.get_current_prefix()]
        if hasattr(form, 'save'):
            if isinstance(form, forms.ModelForm):
                self.object = form.save(commit=commit)
            else:
                form.save()
        return super(MultiModelFormMixin, self).form_valid(form)

    def get_context_data(self, **kwargs):
        """
        If an object has been supplied, inject it into the context with the
        supplied context_object_name name.
        """
        context = {}
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context.update(kwargs)
        return super(MultiModelFormMixin, self).get_context_data(**context)

class ProcessMultiFormView(base.View):
    """
    A mixin that renders a form on GET and processes it on POST.
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        forms = self.get_forms()
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        forms = self.get_forms()
        prefix = self.get_current_prefix()
        if forms[prefix].is_valid():
            return self.form_valid(forms)
        else:
            return self.form_invalid(forms)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

class BaseMultiFormView(MultiFormMixin, ProcessMultiFormView):
    """
    A base view for displaying multiple forms
    """

class MultiFormView(base.TemplateResponseMixin, BaseMultiFormView):
    """
    A base view for displaying multiple forms, and rendering a template reponse.
    """

class BaseMultiUpdateView(MultiModelFormMixin, ProcessMultiFormView):
    """
    Base view for updating an existing object.

    Using this base class requires subclassing to provide a response mixin.
    """
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseMultiUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseMultiUpdateView, self).post(request, *args, **kwargs)

class MultiUpdateView(detail.SingleObjectTemplateResponseMixin, BaseMultiUpdateView):
    """
    View for updating an object,
    with a response rendered by template.
    """
    template_name_suffix = '_form'
