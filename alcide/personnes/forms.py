# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import (inlineformset_factory, modelformset_factory,
        BaseInlineFormSet, BaseModelFormSet)
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from alcide.ressources.models import WorkerType, Service, HolidayType

from models import Worker, UserWorker, TimeTable, Holiday, ExternalTherapist, ExternalWorker


class UserForm(forms.ModelForm):
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    worker = forms.ModelChoiceField(label=_('Personnel'),
            queryset=Worker.objects.filter(enabled=True), empty_label=_('None'),
            required=False)
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."),
        required=False)

    def __init__(self, service=None, *args, **kwargs):
        self.service = service
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = _('Identifiant')
        if self.instance:
            try:
                worker = self.instance.userworker.worker
                self.fields['worker'].initial = worker.pk
            except UserWorker.DoesNotExist:
                pass

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        if self.instance is None:
            try:
                User.objects.get(username=username)
                raise forms.ValidationError(self.error_messages['duplicate_username'])
            except User.DoesNotExist:
                pass
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'worker', 'groups')
        widgets = {
                'groups': forms.CheckboxSelectMultiple,
        }

    def save(self, commit=True):
        instance = super(UserForm, self).save(commit=False)
        if self.cleaned_data['password1']:
            instance.set_password(self.cleaned_data['password1'])
        worker = self.cleaned_data.get('worker')
        if worker is not None:
            instance.first_name = worker.first_name
            instance.last_name = worker.last_name
            def save_m2m():
                qs = UserWorker.objects.filter(user=instance)
                if qs.exists():
                    qs.update(worker=worker)
                else:
                    UserWorker.objects.create(user=instance, worker=worker)
            self.save_m2m = save_m2m
        else:
            try:
                instance.userworker.delete()
            except UserWorker.DoesNotExist:
                pass
        if instance.pk:
            instance.groups = self.cleaned_data['groups']
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class WorkerSearchForm(forms.Form):
    last_name = forms.CharField(label=u'Nom', required=False)
    first_name = forms.CharField(label=u'Prénom', required=False)
    profession = forms.ModelChoiceField(label=u'Profession',
            queryset=WorkerType.objects.all(), required=False)

    INTERVENE_STATUS_CHOICES = {
            'a': u'Actifs',
    }

    intervene_status = forms.MultipleChoiceField(
        choices=INTERVENE_STATUS_CHOICES.iteritems(),
        widget=forms.CheckboxSelectMultiple,
        initial=INTERVENE_STATUS_CHOICES.keys(),
        required=False)

class WorkerIdForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ('last_name', 'first_name', 'initials', 'gender', 'type', 'enabled')
        widgets = {
                'initials': forms.TextInput(attrs={'size': 6}),
                }

class WorkerServiceForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ('services',)
        widgets = {
                'services': forms.CheckboxSelectMultiple,
        }

PERIOD_LIST_TO_FIELDS = [(1, None, None),
(2, None, None),
(3, None, None),
(4, None, None),
(5, None, None),
(None, 0, None),
(None, 1, None),
(None, 2, None),
(None, 3, None),
(None, 4, None),
(None, None, 0),
(None, None, 1)
]

class BaseTimeTableForm(forms.ModelForm):
    class Meta:
        model = TimeTable
        widgets = {
                'services': forms.CheckboxSelectMultiple,
                'week_period': forms.HiddenInput(),
                'week_parity': forms.HiddenInput(),
                'week_rank': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super(BaseTimeTableForm, self).clean()
        msg = None
        if not cleaned_data.get('periodicity'):
            msg = u"Périodicité manquante."
        else:
            try:
                periodicity = int(cleaned_data.get('periodicity'))
                if periodicity:
                    if periodicity < 1 or periodicity > 12:
                        msg = u"Périodicité inconnue."
                    else:
                        cleaned_data['week_period'], \
                        cleaned_data['week_rank'], \
                        cleaned_data['week_parity'] = PERIOD_LIST_TO_FIELDS[periodicity - 1]
            except:
                msg = u"Périodicité invalide."
        if msg:
            self._errors["periodicity"] = self.error_class([msg])
        return cleaned_data

TimetableFormSet = inlineformset_factory(Worker, TimeTable,
        form=BaseTimeTableForm,
        fields=('start_time', 'end_time', 'start_date', 'end_date',
            'services', 'periodicity', 'week_period', 'week_parity', 'week_rank'))

class BaseHolidayForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseHolidayForm, self).__init__(*args, **kwargs)
        self.fields['holiday_type'].queryset = \
                HolidayType.objects.filter(for_group=False)
    class Meta:
        widgets = {
                'comment': forms.Textarea(attrs={'rows': 3}),
        }

class HolidayForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HolidayForm, self).__init__(*args, **kwargs)
        self.fields['holiday_type'].queryset = \
            HolidayType.objects.filter(for_group=False)

    class Meta:
        model = Holiday
        widgets = {
            'comment': forms.Textarea(attrs = {'rows': 3, 'cols': 18}),
            'start_date': forms.DateInput(format = '%d/%m/%Y',
                                          attrs = {'size': 10}),
            'end_date': forms.DateInput(format = '%d/%m/%Y',
                                        attrs = {'size': 10}),
            }

    def clean(self):
        cleaned_data = super(HolidayForm, self).clean()
        if cleaned_data.get('start_date') and cleaned_data.get('end_date'):
            if cleaned_data['start_date'] > cleaned_data['end_date']:
                raise forms.ValidationError(u'La date de début doit être supérieure à la date de fin')
        return cleaned_data

HolidayFormSet = inlineformset_factory(
        Worker, Holiday,
        form=BaseHolidayForm,
        fields=('start_date', 'end_date', 'start_time', 'end_time', 'holiday_type', 'comment'))

class HolidaySearchForm(forms.Form):
    start_date = forms.DateField(required=False, localize=True)
    end_date = forms.DateField(required=False, localize=True)

    def clean(self):
        cleaned_data = super(HolidaySearchForm, self).clean()
        if cleaned_data.get('start_date') and cleaned_data.get('end_date'):
            if cleaned_data['start_date'] > cleaned_data['end_date']:
                raise forms.ValidationError(u'La date de début doit être supérieure à la date de fin')
        return cleaned_data

class GroupHolidayBaseFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.service = kwargs.pop('service', None)
        old_form = self.form
        self.form = lambda *args, **kwargs: old_form(*args, service=self.service, **kwargs)
        super(GroupHolidayBaseFormSet, self).__init__(*args, **kwargs)

class GroupHolidayForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.service = kwargs.pop('service', None)
        super(GroupHolidayForm, self).__init__(*args, **kwargs)
        self.fields['holiday_type'].queryset = \
                HolidayType.objects.filter(for_group=True)

    class Meta:
        model = Holiday
        widgets = {
            'comment': forms.Textarea(attrs = {'rows': 3, 'cols': 18}),
            'services': forms.CheckboxSelectMultiple()
        }

GroupHolidayFormSet = modelformset_factory(Holiday,
        can_delete=True,
        form=GroupHolidayForm,
        formset=GroupHolidayBaseFormSet,
        fields=('start_date', 'end_date', 'start_time', 'end_time', 'holiday_type', 'comment'))
