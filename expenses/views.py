#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.shortcuts import render
from expenses.forms import BillForm

def normal_bill_form(request):
    if request.POST:
        print("c'est bien un post")
        submitted_form = BillForm(request.POST)
        if submitted_form.is_valid():
            print('lollolol')
            submitted_form.save()
            render(request, 'thanks.html')
    return render(request, 'index.html', {'form':BillForm(request.POST)})
