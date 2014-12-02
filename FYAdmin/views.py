# coding=utf-8
# Date: 14/11/30
# Time: 19:20
# Email:fanjunwei003@163.com

import base64
from functools import update_wrapper
import os
import random
from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.utils.decorators import classonlymethod
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin
import time
from FYAdmin.forms import *
from FYAdmin.models import *
from django.utils.http import urlencode
from util.tools import *

__author__ = u'范俊伟'

DOT = '.'
PREVIOUS_PAGE = '<'
NEXT_PAGE = '>'


def get_img_code(request):
    string = '12345679ACEFGHKMNPRTUVWXY'
    ImageCode_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools', 'ImageCode.jar').replace('\\',
                                                                                                                '/')
    code = ''.join(random.sample(string, 4))
    request.session['login_img_code'] = code.lower()
    res = os.popen('java -jar ' + ImageCode_path + ' ' + code)
    data = base64.decodestring(res.read())
    return HttpResponse(data, 'image/png')


tradingLimitLock = threading.RLock()


def trading_limit(request):
    tradingLimitLock.acquire()
    try:
        goodsID = request.REQUEST.get('id')
        if hasattr(request.user, 'fyuserprofile'):
            checked, res = fy_api.trading_limit(request.user.fyuserprofile.fy_username,
                                                request.user.fyuserprofile.fy_password, goodsID)

            if checked:
                if res < 10:
                    html = format_html(u'<span style="color:red">{0}</span>', res)
                else:
                    html = format_html(u'<span>{0}</span>', res)
                return HttpResponse(html, 'text/html')
            else:
                raise Http404(res)
        else:
            raise Http404(u'未设置泛亚账户')
    finally:
        tradingLimitLock.release()


def logout(request):
    auth_logout(request)
    return http.HttpResponseRedirect(request.REQUEST.get('next', reverse('fyadmin:home')))


def admin_view_decorator(func):
    def admin_view(cls, cached=False, **kwargs):
        view = func(cls, **kwargs)

        def has_permission(request):
            if request.user.is_active:
                return True
            else:
                return False

        def inner(request, *args, **kwargs):
            if not has_permission(request) and getattr(view, 'need_site_permission', True):
                return LoginView.as_view()(request, *args, **kwargs)
            return view(request, *args, **kwargs)

        if not cached:
            inner = never_cache(inner)
        return update_wrapper(inner, view)

    return admin_view


class BaseView(TemplateView):
    need_site_permission = True
    template_name = 'fyadmin/base.html'

    def get_context_data(self, **kwargs):
        kwargs = super(BaseView, self).get_context_data(**kwargs)
        kwargs['url'] = self.request.get_full_path()
        if hasattr(self, 'form'):
            kwargs['form'] = self.form
        return kwargs

    def get_query_string(self, new_params=None, remove=None):
        if new_params is None:
            new_params = {}
        if remove is None:
            remove = []
        p = dict(self.request.GET.items()).copy()
        for r in remove:
            for k in p.keys():
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        qs = urlencode(p)
        if qs:
            return '?%s' % qs
        else:
            return ''

    @classonlymethod
    @admin_view_decorator
    def as_view(cls, **initkwargs):
        return super(BaseView, cls).as_view(**initkwargs)


class LoginView(BaseView):
    template_name = 'fyadmin/login.html'


    @classonlymethod
    def as_view(cls, **initkwargs):
        return super(BaseView, cls).as_view(**initkwargs)

    def post(self, request, *args, **kwargs):
        self.form = LoginForm(request=request, data=request.POST)
        if self.form.is_valid():
            auth_login(request, self.form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return http.HttpResponseRedirect(request.REQUEST.get('next', request.get_full_path()))
        else:
            return self.get(request, *args, **kwargs)


class RegisterView(BaseView):
    need_site_permission = False
    template_name = 'fyadmin/register.html'


    @classonlymethod
    def as_view(cls, **initkwargs):
        return super(BaseView, cls).as_view(**initkwargs)

    def post(self, request, *args, **kwargs):
        self.form = RegisterForm(request=request, data=request.POST)
        if self.form.is_valid():
            self.form.save()
            return http.HttpResponseRedirect(request.REQUEST.get('next', reverse('fyadmin:home')))
        else:
            return self.get(request, *args, **kwargs)


class FrameView(BaseView):
    def get_site_menu(self):
        return [
            {'title': u'账户信息', 'menus':
                [
                    {'title': u'我的资金',
                     'icon': 'glyphicon-star',
                     'url': reverse('fyadmin:cash_summary')},
                    {'title': u'未成交查询',
                     'icon': 'glyphicon-star',
                     'url': reverse('fyadmin:pending_orders')},
                ],

            },

            {'title': u'资金受托', 'menus':
                [
                    {'title': u'资金配比',
                     'icon': 'glyphicon-star',
                     'url': reverse('fyadmin:money_supply')},
                ],

            },
        ]

    def get_context_data(self, **kwargs):
        kwargs = super(FrameView, self).get_context_data(**kwargs)
        kwargs['nav_menu'] = self.get_site_menu()
        return kwargs

    template_name = 'fyadmin/frame.html'


class BaseListView(MultipleObjectMixin, FrameView):
    paginate_by = 100


    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(BaseListView, self).get(request, *args, **kwargs)

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        paginator = super(BaseListView, self).get_paginator(queryset, per_page, orphans=0,
                                                            allow_empty_first_page=True, **kwargs)
        page = self.kwargs.get(self.page_kwarg) or self.request.GET.get(self.page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                page_number = 0

        new_page_number = page_number

        if page_number < 1:
            new_page_number = 1
        elif page_number > paginator.num_pages:
            new_page_number = paginator.num_pages
        if new_page_number != page_number:
            self.kwargs[self.page_kwarg] = new_page_number
        return paginator

    def get_page_number(self, i):
        if i == PREVIOUS_PAGE:
            if self.page_num > 1:
                return mark_safe(u'<li><a href="%s">&laquo;</a></li> ' % (
                    escape(self.get_query_string({self.page_kwarg: self.page_num - 1}))))
            else:
                return mark_safe(u'<li class="disabled"><span >&laquo;</span></li> ')
        elif i == NEXT_PAGE:
            if self.page_num < self.paginator.num_pages:
                return mark_safe(u'<li><a href="%s">&raquo;</a></li> ' % (
                    escape(self.get_query_string({self.page_kwarg: self.page_num + 1}))))
            else:
                return mark_safe(u'<li class="disabled"><span >&raquo;</span></li> ')
        elif i == DOT:
            return mark_safe(u'<li><span class="dot-page">...</span></li>')
        elif i == self.page_num:
            return mark_safe(u'<li class="active"><span>%d</span></li> ' % i)
        else:
            return mark_safe(u'<li><a href="%s">%d</a></li> ' % (
                escape(self.get_query_string({self.page_kwarg: i})), i))

    def page_range(self, paginator, page_num, page_type='normal'):
        """
        Generates the series of links to the pages in a paginated list.
        """

        ON_EACH_SIDE = {'normal': 5, 'small': 3}.get(page_type, 3)
        ON_ENDS = 2
        self.paginator = paginator
        self.page_num = page_num
        total_pages_num = paginator.num_pages
        # If there are 10 or fewer pages, display links to every page.
        # Otherwise, do some fancy
        if total_pages_num <= 10:
            page_range = range(1, total_pages_num + 1)
        else:
            # Insert "smart" pagination links, so that there are always ON_ENDS
            # links at either end of the list of pages, and there are always
            # ON_EACH_SIDE links at either end of the "current page" link.
            page_range = []
            if page_num > (ON_EACH_SIDE + ON_ENDS):
                page_range.extend(range(1, ON_EACH_SIDE))
                page_range.append(DOT)
                page_range.extend(
                    range(page_num - ON_EACH_SIDE, page_num + 1))
            else:
                page_range.extend(range(1, page_num + 1))
            if page_num < (total_pages_num - ON_EACH_SIDE - ON_ENDS - 1):
                page_range.extend(
                    range(page_num + 1, page_num + ON_EACH_SIDE + 1))
                page_range.append(DOT)
                page_range.extend(range(
                    total_pages_num - ON_ENDS, total_pages_num + 1))
            else:
                page_range.extend(range(page_num + 1, total_pages_num + 1))

        page_range.insert(0, PREVIOUS_PAGE)
        page_range.append(NEXT_PAGE)
        return {
            'page_range': map(self.get_page_number, page_range),
        }

    def get_context_data(self, **kwargs):
        kwargs = super(BaseListView, self).get_context_data(**kwargs)
        is_paginated = kwargs.get('is_paginated', False)
        if is_paginated:
            paginator = kwargs.get('paginator')
            page_obj = kwargs.get('page_obj')
            kwargs.update(self.page_range(paginator, page_obj.number))
        return kwargs


class FrameFormView(FormMixin, FrameView):
    exclude = None
    fields = None

    def get(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        if not hasattr(self, 'form') or not self.form:
            self.form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=self.form))

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        if self.form.is_valid():
            return self.form_valid(request, *args, **kwargs)
        else:
            return self.form_invalid(request, *args, **kwargs)

    def get_object_instance(self):
        return None

    def get_form_kwargs(self):
        kwargs = super(FrameFormView, self).get_form_kwargs()
        kwargs['request'] = self.request
        instance = self.get_object_instance()
        if instance:
            kwargs['instance'] = instance
        return kwargs

    def form_valid(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def form_invalid(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_field_attrs(self, db_field, **kwargs):
        return {}

    def formfield_for_dbfield(self, db_field, **kwargs):

        attrs = self.get_field_attrs(db_field, **kwargs)
        formfield = db_field.formfield(**dict(attrs, **kwargs))

        if isinstance(db_field, models.ManyToManyField) or isinstance(db_field, models.ForeignKey) or isinstance(
                db_field, models.OneToOneField):
            if 'user_id' in db_field.rel.to._meta.get_all_field_names():
                formfield.queryset = formfield.queryset.filter(user_id=self.request.user.pk)
            if 'user' in db_field.rel.to._meta.get_all_field_names():
                formfield.queryset = formfield.queryset.filter(user=self.request.user)

        return formfield


    def get_model_form(self, form, model, **kwargs):
        defaults = {
            "form": form,
            "fields": self.fields and list(self.fields) or None,
            "exclude": self.exclude,
            "formfield_callback": self.formfield_for_dbfield,
        }
        defaults.update(kwargs)
        from django.forms.models import modelform_factory

        return modelform_factory(model, **defaults)

    def get_form(self, form_class):

        if issubclass(form_class, forms.ModelForm) and hasattr(form_class, 'Meta') and hasattr(form_class.Meta,
                                                                                               'model') and form_class.Meta.model:
            form_class = self.get_model_form(form_class, form_class.Meta.model)
        form = super(FrameFormView, self).get_form(form_class)
        return form


class HomeView(FrameView):
    template_name = 'fyadmin/home.html'
    title = u'主页'


class ChangePasswordView(FrameFormView):
    template_name = 'fyadmin/change_password.html'
    title = u'修改密码'
    form_class = ChangePasswordForm

    def form_valid(self, request, *args, **kwargs):
        self.form.save()
        messages.success(request, '修改成功')
        return self.get(request, *args, **kwargs)


class ChangeFYView(FrameFormView):
    template_name = 'fyadmin/change_fy.html'
    title = u'修改泛亚账号'
    form_class = ChangeFYForm

    def form_valid(self, request, *args, **kwargs):
        self.form.save()
        messages.success(request, '修改成功')
        return self.get(request, *args, **kwargs)


def appendMoneyItem(json_data, object_list, name, value_key):
    try:
        object_list.append((name, format(float(json_data.get(value_key)) / 100.0, ',.2f')))
    except:
        pass


class CashSummaryView(FrameView):
    template_name = 'fyadmin/cash_summary.html'
    title = u'我的资金'

    def get_context_data(self, **kwargs):
        if hasattr(self.request.user, 'fyuserprofile'):
            checked, res = fy_api.cash_summary(self.request.user.fyuserprofile.fy_username,
                                               self.request.user.fyuserprofile.fy_password)
            if checked:
                object_list = []
                appendMoneyItem(res, object_list, u'期初资金', 'initialBalance')
                appendMoneyItem(res, object_list, u'期末资金', 'currentBalance')
                appendMoneyItem(res, object_list, u'应追加资金', 'depositExpected')
                appendMoneyItem(res, object_list, u'当日入金', 'deposit')
                appendMoneyItem(res, object_list, u'可出资金', 'withdrawable')
                object_list.append(None)
                appendMoneyItem(res, object_list, u'总可用资金', 'available')
                appendMoneyItem(res, object_list, u'资金权益', 'cashValue')
                appendMoneyItem(res, object_list, u'货物权益', 'goodsValue')
                data = {
                    'object_list': object_list
                }
                kwargs.update(data)
            else:
                messages.error(self.request, res)
        else:
            messages.error(self.request, u'未设置泛亚账户')
        return super(CashSummaryView, self).get_context_data(**kwargs)


class PendingOrdersView(FrameView):
    template_name = 'fyadmin/pending_orders.html'
    title = u'未成交查询'

    def post(self, request, *args, **kwargs):
        selected_ids = request.REQUEST.getlist('id')
        if '__action_delete' in request.POST:
            if hasattr(self.request.user, 'fyuserprofile'):
                fy_username = self.request.user.fyuserprofile.fy_username
                fy_password = self.request.user.fyuserprofile.fy_password

                error = False
                if selected_ids:
                    for id in selected_ids:
                        checked, res = fy_api.cancel_order(fy_username, fy_password, id)
                        if not checked:
                            error = True
                            messages.error(request, res)
                    if not error:
                        messages.success(request, u'撤销成功成功')
                else:
                    messages.error(request, u'未选择')
            else:
                messages.error(self.request, u'未设置泛亚账户')

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if hasattr(self.request.user, 'fyuserprofile'):
            checked, res = fy_api.pending_orders(self.request.user.fyuserprofile.fy_username,
                                                 self.request.user.fyuserprofile.fy_password)
            if checked:
                data = {
                    'object_list': res
                }
                kwargs.update(data)
            else:
                messages.error(self.request, res)
        else:
            messages.error(self.request, u'未设置泛亚账户')
        return super(PendingOrdersView, self).get_context_data(**kwargs)


class MoneySupplyView(FrameView):
    template_name = 'fyadmin/money_supply.html'
    title = u'资金配比'

    def get_context_data(self, **kwargs):
        cache_key = 'money_supply_view'
        data = cache.get(cache_key)
        if not data:
            checked, res = fy_api.all_googds()
            if checked:
                moneySupplyRequestedTotal = 0
                moneySupplyTotal = 0

                object_list = []
                for item in res:
                    goodsId = item.get('goodsId')
                    goodsName = item.get('goodsName')
                    try:
                        checked, googdsInfo = fy_api.get_money_info(goodsId, goodsName)
                        if checked:
                            if googdsInfo['moneySupplyRequested']:
                                moneySupplyRequestedTotal += int(googdsInfo['m1'])
                            if googdsInfo['moneySupply']:
                                moneySupplyTotal += int(googdsInfo['m2'])
                            '''
                            if hasattr(self.request.user, 'fyuserprofile'):
                                checked, res = fy_api.trading_limit(self.request.user.fyuserprofile.fy_username,
                                                                    self.request.user.fyuserprofile.fy_password,
                                                                    goodsId)

                                if checked:
                                    if res < 10:
                                        html = format_html(u'<span style="color:red">{0}</span>', res)
                                    else:
                                        html = format_html(u'<span>{0}</span>', res)
                                    googdsInfo['limit'] = html
                            '''
                            object_list.append(googdsInfo)
                    except Exception:
                        pass
                object_list.sort(fy_api.goods_CMP)
                mf1 = format(moneySupplyRequestedTotal / 100000000.0, ',.2f')
                mf2 = format(moneySupplyTotal / 100000000.0, ',.2f')
                data = {
                    'object_list': object_list,
                }
                cache.set(cache_key, data)
                kwargs.update(data)
            else:
                messages.error(self.request, res)
        else:
            kwargs.update(data)

        return super(MoneySupplyView, self).get_context_data(**kwargs)


class LendingOrderView(FrameFormView):
    template_name = 'fyadmin/lend_order.html'
    title = u'资金受托'
    form_class = LendOrderForm

    def form_valid(self, request, *args, **kwargs):
        self.form.save()
        messages.success(request, '修改成功')
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        goodsId = self.kwargs.get('goodsId')
        data = {}
        try:
            checked, goodsInfo = fy_api.get_money_info(goodsId, None)
            if checked:
                data['id'] = goodsInfo.get('id')
                data['ratio_format'] = goodsInfo.get('ratio_format') + '%'
                data['moneySupplyRequested'] = goodsInfo.get('moneySupplyRequested')
                data['moneySupply'] = goodsInfo.get('moneySupply')
                data['recommendation'] = goodsInfo.get('recommendation')
                data['financePrice'] = goodsInfo.get('financePrice')
                checked, limit = fy_api.trading_limit(self.request.user.fyuserprofile.fy_username,
                                                      self.request.user.fyuserprofile.fy_password,
                                                      goodsId)
                if checked:
                    data['limit'] = limit
                checked, limit_end = fy_api.trading_limit(self.request.user.fyuserprofile.fy_username,
                                                          self.request.user.fyuserprofile.fy_password,
                                                          goodsId, 'money_end')
                if checked:
                    data['limit_end'] = limit_end
            kwargs.update(data)
        except Exception:
            pass
        return super(LendingOrderView, self).get_context_data(**kwargs)