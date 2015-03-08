#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from expenses.models import Bill, ExtendedUser
from django.contrib.auth.models import User

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
