from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from models import Worker, UserWorker

class UserForm(forms.ModelForm):
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    worker = forms.ModelChoiceField(label=_('Personnel'),
            queryset=Worker.objects.all(), empty_label=_('None'),
            required=False)
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    def __init__(self, service=None, *args, **kwargs):
        self.service = service
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['worker'].queryset = Worker.objects.for_service(service)
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
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'worker')

    def save(self, commit=True):
        instance = super(UserForm, self).save(commit=False)
        if self.cleaned_data['password1']:
            instance.set_password(self.cleaned_data['password1'])
        worker = self.cleaned_data.get('worker')
        if worker is not None:
            self.first_name = worker.first_name
            self.last_name = worker.last_name
            def save_m2m(self):
                try:
                    userworker = self.instance.userworker
                    userworker.worker = worker
                    userworker.save()
                except UserWorker.DoesNotExist:
                    UserWorker.objects.create(id=self.id, worker=worker)
            self.save_m2m = save_m2m
        else:
            self.save_m2m = lambda self: None
        if commit:
            instance.save()
        return instance

#class CreateCongeAnnuelForm(ModelForm):
#    class Meta:
#        model = CongeAnnuel
#
#
#class EditCongeAnnuelForm(ModelForm):
#    class Meta:
#        model = CongeAnnuel
