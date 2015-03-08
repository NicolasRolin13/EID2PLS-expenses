#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from expenses.models import Bill, ExtendedUser


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
#        self.fields['receivers'].widget.attrs['size'] = min(len(self.fields), 10)


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
