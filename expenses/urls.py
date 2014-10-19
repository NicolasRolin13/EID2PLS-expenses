#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
import expenses.views

urlpatterns = patterns('',
            url(r'^$', expenses.views.test),
            )
