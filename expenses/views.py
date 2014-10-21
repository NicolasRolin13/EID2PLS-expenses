#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.shortcuts import render
from expenses.forms import BillForm

def normal_bill_form(request):
    if request.POST:
        submitted_form = BillForm(request.POST)
        if submitted_form.is_valid():
            bill_model = submitted_form.save(commit=False)
            cleaned_form = submitted_form.cleaned_data
            bill_model.unsafe_save()
            bill_model.create_transferts(cleaned_form['buyer'], cleaned_form['receivers'])
            bill_model.save()
            render(request, 'thanks.html')
    return render(request, 'index.html', {'form':BillForm(request.POST)})
