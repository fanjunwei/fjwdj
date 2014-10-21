import mimetypes
import os
import stat
import uuid
from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, render_to_response
from django.template.response import TemplateResponse
from django.utils.http import http_date
from django.views.static import was_modified_since

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from fy_query import *

# Create your views here.

def home(request):
    return TemplateResponse(request, 'home.html', locals())


def moneySupply(request):
    res = []
    moneySupplyRequestedTotal = 0
    moneySupplyTotal = 0
    for k, v in GoodsIds.items():
        try:
            googdsInfo = getMoneyInfo(k)
            if googdsInfo['moneySupplyRequested']:
                moneySupplyRequestedTotal += int(googdsInfo['m1'])
            if googdsInfo['moneySupply']:
                moneySupplyTotal += int(googdsInfo['m2'])
            res.append(googdsInfo)
        except Exception:
            pass
    res.sort(GoodsCMP)
    mf1 = format(moneySupplyRequestedTotal / 100000000.0, ',.2f')
    mf2 = format(moneySupplyTotal / 100000000.0, ',.2f')
    if moneySupplyRequestedTotal <= 0 or moneySupplyTotal <= 0:
        dataError = True
    else:
        dataError = False
    return TemplateResponse(request, 'moneySupply.html', locals())