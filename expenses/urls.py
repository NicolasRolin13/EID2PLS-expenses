#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import url

from django.contrib.auth.views import login, logout

from expenses import views
from expenses.forms import BillForm, CustomSplitForm, EmptyForm

urlpatterns = [
    url(r'^$', views.view_root),
    url(r'^bill/create/?$', views.WizardBillView.as_view([BillForm, CustomSplitForm, EmptyForm]), name='wizard_bill_form'),
    url(r'^bill/view/(?P<bill_id>\d+)/?$', views.display_bill, name='display_bill'),
    url(r'^bill/refund/?$', views.RepaymentView.as_view(), name='refund_form'),
    url(r'^accounts/create/?$', views.UserCreateView.as_view(), name='user_create'),
    url(r'^accounts/edit/?$', views.UserEditView.as_view(), name='user_edit'),
    url(r'^accounts/login/?$', login, name='login'),
    url(r'^accounts/logout/?$', logout, name='logout'),
    url(r'^accounts/history/?$', views.view_account_history, name='account_history'),
    url(r'^whatsnew/?$', views.whats_new),
    url(r'^home/?$', views.view_home, name='home'),
    url(r'^balances/?$', views.view_balances, name='balances'),
    url(r'^history/(?P<history_id>\d+)/?$', views.view_history, name='history'),
    ]
