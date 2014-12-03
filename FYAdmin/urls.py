# coding=utf-8
# Date: 14/11/21
# Time: 09:11
# Email:fanjunwei003@163.com
from django.conf.urls import patterns, url
from views import *

__author__ = u'范俊伟'

urlpatterns = patterns('fyadmin',
                       url(r'^img_code/$', get_img_code, name='img_code'),
                       url(r'^trading_limit/$', trading_limit, name='trading_limit'),
                       url(r'^register/$', RegisterView.as_view(), name='register'),
                       url(r'^logout/$', logout, name='logout'),
                       url(r'^$', HomeView.as_view(), name='home'),
                       url(r'^change_password/$', ChangePasswordView.as_view(), name='change_password'),
                       url(r'^change_fy/$', ChangeFYView.as_view(), name='change_fy'),
                       url(r'^cash_summary/$', CashSummaryView.as_view(), name='cash_summary'),
                       url(r'^pending_orders/$', PendingOrdersView.as_view(), name='pending_orders'),
                       url(r'^consolidated/$', ConsolidatedView.as_view(), name='consolidated'),
                       url(r'^money_supply/$', MoneySupplyView.as_view(), name='money_supply'),
                       url(r'^lend_order/(?P<goodsId>\w*?)$', LendingOrderView.as_view(), name='lend_order'),
                       url(r'^task_edit/$', TaskEditView.as_view(), name='task_edit'),
                       url(r'^task_log_list/$', TaskLogListView.as_view(), name='task_log_list'),
)
