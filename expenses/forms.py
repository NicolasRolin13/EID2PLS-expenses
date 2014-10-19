#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from expenses.models import Bill, Transfert, ExtendedUser

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
#        fields = ['category', 'amount', 'title', 'description']
        exclude = ['creator', 'date', 'repayment']
    buyer = forms.ModelChoiceField(queryset=ExtendedUser.objects.all())
    receivers = forms.ModelMultipleChoiceField(queryset=ExtendedUser.objects.all())

    def create_transferts(self):
        for receiver in self.receivers:
            transfert = Transfert()
            transfert.amount = self.amount/len(self.receivers)
            transfert.sender = self.buyer
            transfert.receiver = receiver
            child_of_bill = self

            transfert.save()

    def clean(self, *args, **kwargs):
        self.create_transferts()
        super().clean(*args, **kwargs)
