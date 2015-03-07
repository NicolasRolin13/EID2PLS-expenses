#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from expenses.models import Bill, ExtendedUser
from django.contrib.auth.models import User

class BillForm(forms.ModelForm):
    '''
    Form for non-repayment bill.
    '''
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Bill
#        fields = ['category', 'amount', 'title', 'description']
        exclude = ['creator', 'date', 'repayment']

    buyer = forms.ModelMultipleChoiceField(queryset=User.objects.all())
    receivers = forms.ModelMultipleChoiceField(queryset=User.objects.all())


class RepaymentForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Bill
        fields = ['amount']

    buyer = forms.ModelChoiceField(queryset=ExtendedUser.objects.all())
    receiver = forms.ModelChoiceField(queryset=ExtendedUser.objects.all())
