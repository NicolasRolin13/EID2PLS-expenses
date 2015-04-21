#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.views.generic.edit import FormView
from django.contrib.formtools.wizard.views import SessionWizardView
from django.forms.models import formset_factory

from expenses.forms import BillForm, RepaymentForm, ExtendedUserCreationForm, CustomSplitForm
from expenses.models import Atom, Bill, ExtendedUser


# Bill related
###################

class WizardBillView(SessionWizardView):
    TEMPLATES = {'0': 'bill_wizard/bill_form.html',
        '1': 'bill_wizard/split.html',
        '2': 'bill_wizard/bill_form.html'}

    def get_template_names(self):
        return self.TEMPLATES[self.steps.current]

    def get_form(self, step=None, data=None, files=None):
        base_form = super().get_form(step, data, files)
        if step is None:
            step = self.steps.current

        if step != '0':
            base_data = self.get_cleaned_data_for_step('0')
            receivers = base_data['receivers']

        if step == '1':
            num = len(receivers)
            BillFormset = formset_factory(CustomSplitForm, max_num=num, min_num=num, validate_max=True, validate_min=True)
            formset = BillFormset(data)
            for (form, user) in zip(formset, receivers):
                form.user = user
            return formset

        else:
            return base_form

    def done(self, form_list, form_dict, **kwargs):
        bill_model = form_dict['0'].save(commit=False)
        bill_model.creator = self.request.user.extendeduser

        bill_model.unsafe_save()

        for form in form_dict['1']:
            atom_model = form.save(commit=False)
            atom_model.child_of_bill = bill_model
            atom_model.save()
        bill_model.update_amount()
        try:
            bill_model.save()
        except ValidationError:
            bill_model.delete()

        return redirect('home')


class NormalBillView(FormView):
    template_name = 'basic_form.html'
    form_class = BillForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        bill_model = form.save(commit=False)
        bill_model.creator = self.request.user.extendeduser
        cleaned_form = form.cleaned_data

        bill_model.unsafe_save()
        bill_model.create_atoms(cleaned_form['buyer'], cleaned_form['receivers'])
        bill_model.update_amount()
        try:
            bill_model.save()
        except ValidationError:
            bill_model.delete()
        return super().form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@login_required
def display_bill(request, bill_id):
    """
    Returns a presentation page for the ```Bill``` instance corresponding to ```bill_id```.
    """
    bill = get_object_or_404(Bill, pk=bill_id)
    return render(request, 'display_bill.html', {'bill': bill})


class RepaymentView(FormView):
    template_name = 'repayment_form.html'
    form_class = RepaymentForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        repayment_model = form.save(commit=False)
        repayment_model.repayment = True
        repayment_model.creator = self.request.user.extendeduser
        repayment_model.title = repayment_model.repayment_name()
        cleaned_form = form.cleaned_data

        repayment_model.unsafe_save()
        repayment_model.create_atoms(cleaned_form['buyer'], cleaned_form['receiver'], True)
        repayment_model.update_amount()
        try:
            repayment_model.save()
        except ValidationError:
            repayment_model.delete()
        return super().form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


# User management
###################

class UserCreateView(FormView):
    template_name = 'user_create_form.html'
    form_class = ExtendedUserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


# Others
###################

def view_root(request):
    if request.user.is_authenticated():
        return redirect('home')
    else:
        return render(request, 'root.html')

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
    Contains the user ```balance``` and the last 5 bills registered.
    """
    status = 'neutral'
    if request.user.extendeduser.balance < 0:
        status = 'negative'
    elif request.user.extendeduser.balance > 0:
        status = 'positive'
    balance = request.user.extendeduser.balance
    last_bills = Bill.objects.all().order_by('-id')[:5]
    return render(request, 'home.html', {'balance': balance, 'status': status, 'last_bills': last_bills})


@login_required
def view_balances(request):
    """
    Returns a presentation of the ```balance``` of each users.
    """
    users = ExtendedUser.objects.all()
    return render(request, 'balances.html', {'users': users})
