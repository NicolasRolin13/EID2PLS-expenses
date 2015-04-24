#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import url

from expenses import views
from expenses.forms import BillForm, CustomSplitForm, EmptyForm

urlpatterns = [
    url(r'^$', views.view_root),
    url(r'^bill/create/?$', views.WizardBillView.as_view([BillForm, CustomSplitForm, EmptyForm]), name='wizard_bill_form'),
    url(r'^bill/view/(?P<bill_id>\d+)/?$', views.display_bill, name='display_bill'),
    url(r'^bill/repayment/?$', views.RepaymentView.as_view(), name='repayment_form'),
    url(r'^accounts/create/?$', views.UserCreateView.as_view(), name='user_create'),
    url(r'^accounts/login/?$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/?$', 'django.contrib.auth.views.logout', name='logout'),
    url(r'^accounts/history/?$', views.view_account_history, name='account_history'),
    url(r'^whatsnew/?$', views.whats_new),
    url(r'^home/?$', views.view_home, name='home'),
    url(r'^balances/?$', views.view_balances, name='balances'),
    ]
