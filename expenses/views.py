#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.core.exceptions import ValidationError

from expenses.forms import BillForm, RepaymentForm
from expenses.models import Atom, Bill, ExtendedUser


# Bill related
###############

@login_required
def normal_bill_form(request):
    """
    View handling for non repayment ```Bill```.
    """
    if request.POST:
        form = BillForm(request.POST)
        if form.is_valid():
            bill_model = form.save(commit=False)
            bill_model.creator = request.user.extendeduser
            cleaned_form = form.cleaned_data

            bill_model.unsafe_save()
            bill_model.create_atoms(cleaned_form['buyer'], cleaned_form['receivers'])
            bill_model.update_amount()
            try:
                bill_model.save()
            except ValidationError:
                bill_model.delete()
                render(request, 'basic_form.html', {'form': form})  # TODO handle this properly
            return redirect('home')
    else:
        form = BillForm(initial={'buyer': request.user.extendeduser})
    return render(request, 'basic_form.html', {
                  'form': form,
                  })


@login_required
def display_bill(request, bill_id):
    """
    Returns a presentation page for the ```Bill``` instance corresponding to ```bill_id```.
    """
    bill = get_object_or_404(Bill, pk=bill_id)
    return render(request, 'display_bill.html', {'bill': bill})


@login_required
def repayment_form(request):
    """
    View handling for repayment ```Bill```.
    """
    if request.POST:
        form = RepaymentForm(request.POST)
        if form.is_valid():
            repayment_model = form.save(commit=False)
            repayment_model.repayment = True
            repayment_model.creator = request.user.extendeduser
            repayment_model.title = repayment_model.repayment_name()
            cleaned_form = form.cleaned_data

            repayment_model.unsafe_save()
            repayment_model.create_atoms(cleaned_form['buyer'], cleaned_form['receiver'])
            repayment_model.update_amount()
            try:
                repayment_model.save()
            except ValidationError:
                repayment_model.delete()
                render(request, 'repayment_form.html', {'form': form})  # TODO handle this properly
            return redirect('home')
    else:
        form = RepaymentForm(initial={'buyer': request.user.extendeduser})
    return render(request, 'repayment_form.html', {
                  'form': form,
                  })


# Others
################
@login_required
def view_history(request):
    """
    Returns a presentation of the last 20 operations as a buyer and as a receiver.
    """
    user = request.user.extendeduser
    buyers_atoms = Atom.objects.filter(user=user).filter(amount__gt=0).order_by('-id')[:20]
    receivers_atoms = Atom.objects.filter(user=user).filter(amount__lt=0).order_by('-id')[:20]

    buyers_table = [(elmt.child_of_bill.title, elmt.amount, elmt.date) for elmt in buyers_atoms]
    receivers_table = [(elmt.child_of_bill.title, elmt.amount, elmt.date) for elmt in receivers_atoms]
    return render(request, 'history.html', {'buyers': buyers_table, 'receivers': receivers_table})


@login_required
def whats_new(request):  # TODO: Remove this view ?
    user = request.user.extendeduser
    last_actions = Bill.objects.all().order_by('-id')[:10]
    last_actions_list = [(action, (user in action.list_of_people_involved())) for action in last_actions]
    return render(request, 'whatsnew.html', {'last_actions': last_actions_list})


@login_required
def view_home(request):
    """
    Returns the ```User``` home page.
    Contains the user ```balance``` and the last 10 bills registered.
    """
    status = 'neutral'
    if request.user.extendeduser.balance < 0:
        status = 'negative'
    elif request.user.extendeduser.balance > 0:
        status = 'positive'
    balance = request.user.extendeduser.balance
    last_bills = Bill.objects.all().order_by('-id')[:10]
    return render(request, 'home.html', {'balance': balance, 'status': status, 'last_bills': last_bills})


@login_required
def view_balances(request):
    """
    Returns a presentation of the ```balance``` of each users.
    """
    users = ExtendedUser.objects.all()
    return render(request, 'balances.html', {'users': users})


# Login handling
#################
@login_required
def view_logout(request):
    """
    Returns the logout page.
    """
    logout(request)
    return render(request, 'logout.html')


def view_login(request, error=None):
    """
    Returns the login page.
    """
    if 'next' in request.GET:
        request.session['next_page'] = request.GET['next']
    return render(request, 'login.html', {'error': error})


@sensitive_post_parameters('password')
def do_login(request):
    """
    Handles a login request.
    Returns the ask page if success.
    Returns the login page if not.
    """
    params = {'username': '', 'password': '', 'next_page': '/'}

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
