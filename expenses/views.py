#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.db.models import Q

from expenses.forms import BillForm
from expenses.models import Transfer, Bill

# Custom views
###############

@login_required
def normal_bill_form(request):
    if request.POST:
        submitted_form = BillForm(request.POST)
        if submitted_form.is_valid():
            bill_model = submitted_form.save(commit=False)
            bill_model.creator = request.user.extendeduser
            cleaned_form = submitted_form.cleaned_data

            bill_model.unsafe_save()
            bill_model.create_transfers(cleaned_form['buyer'], cleaned_form['receivers'])
            bill_model.update_amount()
            bill_model.save()
            render(request, 'thanks.html')
    return render(request, 'basic_form.html', {'form':BillForm(request.POST)})

@login_required
def view_history(request):
    user = request.user.extendeduser
    senders_transfers = Transfer.objects.filter(sender=user).order_by('-id')[:20]
    receivers_transfers = Transfer.objects.filter(receiver=user).order_by('-id')[:20]

    senders_table = [(elmt.child_of_bill.title, elmt.amount, elmt.date) for elmt in senders_transfers]
    receivers_table = [(elmt.child_of_bill.title, elmt.amount, elmt.date) for elmt in receivers_transfers]
    return render(request, 'history.html', {'senders':senders_table, 'receivers':receivers_table})

@login_required
def whats_new(request):
    user = request.user.extendeduser
    last_actions = Bill.objects.all().order_by('-id')[:10]
    last_actions_list = [(action, (user in action.list_of_people_involved())) for action in last_actions]
    return render(request, 'whatsnew.html', {'last_actions':last_actions_list})

# Login handling
#################

@login_required
def view_logout(request):
    logout(request)
    return render(request, 'logout.html')

def view_login(request, error=None):
    if 'next' in request.GET:
        request.session['next_page'] = request.GET['next']
    return render(request, 'login.html', {'error' : error})

@sensitive_post_parameters('password')
def do_login(request):
    params = {'username' : '', 'password' : '', 'next_page' : '/'}

    for (key, value) in request.POST.items():
        params[key] = value

    if 'next_page' in request.session:
        if request.session['next_page']:
            params['next_page'] = request.session.pop('next_page')

    user = authenticate(username=params['username'], password=params['password'])
    if user is not None:
        login(request, user)
        return redirect(params['next_page'])
    else:
        request.session['next_page'] = params['next_page']
        return redirect('view_login_fail')

