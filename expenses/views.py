#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.shortcuts import render
from expenses.forms import BillForm

def test(request):
    if request.POST:
        #TODO fill this with something usefull
        pass
    return render(request, 'index.html', {'form':BillForm()})
