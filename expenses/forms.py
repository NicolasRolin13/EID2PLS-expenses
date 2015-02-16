#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from expenses.models import Bill, Transfer, ExtendedUser

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

    buyer = forms.ModelMultipleChoiceField(queryset=ExtendedUser.objects.all())
    receivers = forms.ModelMultipleChoiceField(queryset=ExtendedUser.objects.all())
