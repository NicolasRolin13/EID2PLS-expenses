#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.views.generic.edit import FormView, UpdateView
import django
if django.VERSION[:2] < (1,8):
    from django.contrib.formtools.wizard.views import SessionWizardView
else:
    from formtools.wizard.views import SessionWizardView
from django.forms.models import formset_factory

from expenses.forms import BillForm, RepaymentForm, ExtendedUserCreationForm, UserEditForm, CustomSplitForm, CustomSplitFormSet, EmptyForm
from expenses.models import Atom, Bill, ExtendedUser, User


# Bill related
###################

class WizardBillView(SessionWizardView):
    TEMPLATES = {
        '0': 'bill_wizard/bill_form.html',
        '1': 'bill_wizard/split.html',
        '2': 'bill_wizard/confirmation.html',
    }

    def get_template_names(self):
        return self.TEMPLATES[self.steps.current]

    def get_form(self, step=None, data=None, files=None):
        base_form = super().get_form(step, data, files)
        if step is None:
            step = self.steps.current

        bill = self.instance_dict.get('0', None)
        if step != '0':
            self.base_data = self.get_cleaned_data_for_step('0')
            participants = self.base_data['participants']
            self.total_amount = self.base_data['amount']
        else:
            if bill:
                base_form.initial.update({'participants': bill.list_of_participants()})
            else:
                base_form.initial.update({'buyer': self.request.user.extendeduser})

        if step == '1':
            num = len(participants)
            BillFormset = formset_factory(CustomSplitForm, formset=CustomSplitFormSet, max_num=num, min_num=num, validate_max=True, validate_min=True)
            participants, splitted_amount = zip(*Bill(amount=self.total_amount).equal_split(participants))
            initial = [{'amount': -amount} for amount in splitted_amount]
            formset = BillFormset(self.total_amount, data, initial=initial)
            for (form, user) in zip(formset, participants):
                form.user = user
                try:
                    if not bill:
                        raise Atom.DoesNotExist()
                    prev = -bill.atoms.get(user=user, amount__lte=0).amount
                    form.initial.update({'amount': prev})
                except Atom.DoesNotExist:
                    pass
            self.atom_forms = [form for form in formset]
            return formset
        else:
            return base_form

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        if self.steps.current == '1':
            context.update({'total_amount': self.total_amount})

        if self.steps.current == '2':
            buyer = {'user': self.base_data['buyer'], 'amount': self.base_data['amount']}
            participants = [{'user': form.user, 'amount': form.cleaned_data['amount']} for form in self.atom_forms]
            context.update({'buyer': buyer})
            context.update({'participants': participants})

        return context

    def done(self, form_list, form_dict, **kwargs):
        with form_dict['0'].save(commit=False) as bill_model:
            bill_model.creator = self.request.user.extendeduser
            bill_model.save() #Register the object to the database

            for atom in bill_model.atoms.all():
                atom.delete()

            for form in form_dict['1']:
                atom_model = form.save(commit=False)
                atom_model.amount = -atom_model.amount
                atom_model.child_of_bill = bill_model
                atom_model.save()
            Atom.objects.create(amount=bill_model.amount, user=form_dict['0'].cleaned_data['buyer'], child_of_bill=bill_model)

            bill_model.update_amount()
            bill_model.save()
        return redirect('home')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class NormalBillView(FormView):
    template_name = 'basic_form.html'
    form_class = BillForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        with form.save(commit=False) as bill_model:
            bill_model.creator = self.request.user.extendeduser
            cleaned_form = form.cleaned_data

            bill_model.save()
            bill_model.create_atoms(cleaned_form['buyer'], cleaned_form['participants'])
            bill_model.update_amount()
            bill_model.save()
        return super().form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

@login_required
def edit_bill(request, bill_id):
    bill = get_object_or_404(Bill, pk=bill_id)
    return WizardBillView.as_view([BillForm, CustomSplitForm, EmptyForm],
        instance_dict={
            '0': bill,
    })(request)

@login_required
def display_bill(request, bill_id):
    """
    Returns a presentation page for the ```Bill``` instance corresponding to ```bill_id```.
    """
    bill = get_object_or_404(Bill, pk=bill_id)
    return render(request, 'display_bill.html', {'bill': bill})


class RepaymentView(FormView):
    template_name = 'refund_form.html'
    form_class = RepaymentForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        with form.save(commit=False) as refund_model:
            refund_model.refund = True
            refund_model.creator = self.request.user.extendeduser
            refund_model.title = refund_model.refund_name()
            cleaned_form = form.cleaned_data

            refund_model.save()
            refund_model.create_atoms(cleaned_form['buyer'], cleaned_form['participant'], True)
            refund_model.update_amount()
            refund_model.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial.update({'buyer': self.request.user.extendeduser})
        return initial

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


class UserEditView(UpdateView):
    template_name = 'user_edit_form.html'
    form_class = UserEditForm
    model = User
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        initial.update({'nickname': self.object.extendeduser.nickname})
        return initial

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


# Others
###################

def view_root(request):
    if request.user.is_authenticated():
        return redirect('home')
    else:
        return render(request, 'root.html')

@login_required
def view_account_history(request):
    """
    Returns a presentation of the last 20 operations as a buyer and as a participant.
    """
    user = request.user.extendeduser
    buyers_atoms = Atom.objects.filter(user=user).filter(amount__gt=0).order_by('-id')[:20]
    participants_atoms = Atom.objects.filter(user=user).filter(amount__lt=0).order_by('-id')[:20]

    buyers_table = [(elmt.child_of_bill.title, elmt.amount, elmt.date) for elmt in buyers_atoms]
    participants_table = [(elmt.child_of_bill.title, elmt.amount, elmt.date) for elmt in participants_atoms]
    return render(request, 'account_history.html', {'buyers': buyers_table, 'participants': participants_table})


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

@login_required
def view_history(request, history_id):
    history_id = int(history_id)
    queryset = Bill.objects.all().order_by('-id')[history_id*10:(history_id + 1)*10]
    bills = get_list_or_404(queryset)
    if history_id == 0:
        has_previous = False
    else:
        has_previous = True
    if len(queryset) < 10:
        has_next = False
    else:
        has_next = True
    params = {'bills': bills, 'has_previous': has_previous, 'has_next': has_next, 'id': history_id}
    return render(request, 'history.html', params)
