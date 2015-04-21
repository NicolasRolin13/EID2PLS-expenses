#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from expenses.models import Atom, Bill, ExtendedUser

from django.contrib.auth.forms import UserCreationForm


class BillForm(forms.ModelForm):
    """
    Form for non-repayment ```Bill```.
    """
    buyer = forms.ModelChoiceField(queryset=ExtendedUser.objects.all(), empty_label=None)
    receivers = forms.ModelMultipleChoiceField(queryset=ExtendedUser.objects.all())

    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Bill
        exclude = ['creator', 'date', 'repayment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = 'u-full-width'
        self.fields['amount'].widget.attrs['class'] = 'u-full-width'
        self.fields['title'].widget.attrs['class'] = 'u-full-width'
        self.fields['description'].widget.attrs['class'] = 'u-full-width'
        self.fields['buyer'].widget.attrs['class'] = 'u-full-width'
        self.fields['receivers'].widget.attrs['class'] = 'u-full-width'


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

class EmptyForm(forms.Form):
    pass

class RepaymentForm(forms.ModelForm):
    """
    Form for repayment ```Bill```.
    """
    buyer = forms.ModelChoiceField(queryset=ExtendedUser.objects.all(), empty_label=None)
    receiver = forms.ModelChoiceField(queryset=ExtendedUser.objects.all())

    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Bill
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs['class'] = 'u-full-width'
        self.fields['buyer'].widget.attrs['class'] = 'u-full-width'
        self.fields['receiver'].widget.attrs['class'] = 'u-full-width'


class ExtendedUserCreationForm(UserCreationForm):
    nickname = forms.CharField(max_length=50)

    error_css_class = 'error'
    required_css_class = 'required'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        extended_user = ExtendedUser(user=self.instance, nickname=self.cleaned_data['nickname'])
        extended_user.save()
