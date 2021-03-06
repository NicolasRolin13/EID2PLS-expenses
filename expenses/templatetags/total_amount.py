# -*- coding: utf-8 -*-

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def total_amount(value):
    return sum(bill.amount for bill in value)
