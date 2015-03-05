#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from expenses import views

urlpatterns = patterns('',
            url(r'^$', views.view_home),
            url(r'^bill/?$', views.normal_bill_form, name='normal_bill_form'),
            url(r'^accounts/login/?$', views.view_login, name='view_login'),
            url(r'^accounts/login/fail/?$', views.view_login, {'error' : 1}, name='view_login_fail'),
            url(r'^accounts/do_login/?$', views.do_login),
            url(r'^accounts/logout/?$', views.view_logout),
            url(r'^accounts/history/?$', views.view_history),
            url(r'^whatsnew/?$', views.whats_new),
            url(r'^home/?$', views.view_home, name='home'),
            url(r'^balances/?$', views.view_balances, name='balances'),
            )
