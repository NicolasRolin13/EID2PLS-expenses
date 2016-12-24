#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from expenses.models import Atom, Bill, ExtendedUser

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from django.contrib.admin.widgets import FilteredSelectMultiple


class BillForm(forms.ModelForm):
    """
    Form for non-refund ```Bill```.
    """
    buyer = forms.ModelChoiceField(label=_("Buyer"), queryset=ExtendedUser.objects.all(), empty_label=None)
    participants = forms.ModelMultipleChoiceField(queryset=ExtendedUser.objects.all(), widget=FilteredSelectMultiple("users", False))

    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Bill
        exclude = ['creator', 'date', 'refund', 'category']

    class Media:
        css = {
            'all':['admin/css/widgets.css',]
        }
        # Adding this javascript is crucial
        js = ['/admin/jsi18n/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
#       self.fields['category'].widget.attrs['class'] = 'u-full-width'
        self.fields['amount'].widget.attrs['class'] = 'u-full-width'
        self.fields['title'].widget.attrs['class'] = 'u-full-width'
        self.fields['description'].widget.attrs['class'] = 'u-full-width'
        self.fields['buyer'].widget.attrs['class'] = 'u-full-width'
        self.fields['participants'].widget.attrs['class'] = 'u-full-width'


class CustomSplitForm(forms.ModelForm):
    class Meta:
        model = Atom
        fields = ('amount', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def save(self, commit=True, *args, **kwargs):
        if commit == False:
            model = super().save(commit=False, *args, **kwargs)
            model.user = self.user
            return model
        else:
            super().save(commit=True, *args, **kwargs)


class CustomSplitFormSet(forms.formsets.BaseFormSet):
    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        total_amount = sum([form.cleaned_data['amount'] for form in self.forms])
        if self.total_amount != total_amount:
            validation_message = "Sum of user amounts (%(total_amount_user)s) doesn't match the bill amount (%(total_amount)s)" % {
                'total_amount_user': total_amount,
                'total_amount': self.total_amount,
            }
            raise forms.ValidationError(validation_message)

    def __init__(self, total_amount, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_amount = total_amount


class EmptyForm(forms.Form):
    pass


class RepaymentForm(forms.ModelForm):
    """
    Form for refund ```Bill```.
    """
    buyer = forms.ModelChoiceField(label='From', queryset=ExtendedUser.objects.all(), empty_label=None)
    participant = forms.ModelChoiceField(label='To', queryset=ExtendedUser.objects.all())

    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Bill
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs['class'] = 'u-full-width'
        self.fields['buyer'].widget.attrs['class'] = 'u-full-width'
        self.fields['participant'].widget.attrs['class'] = 'u-full-width'


class ExtendedUserCreationForm(UserCreationForm):
    error_css_class = 'error'
    required_css_class = 'required'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        extended_user = ExtendedUser(user=self.instance)
        extended_user.save()

class UserEditForm(forms.ModelForm):
    nickname = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self, *args, **kwargs):
            model = super().save(*args, **kwargs)
            model.extendeduser.nickname = self.cleaned_data['nickname']
            model.extendeduser.save()
            return model
