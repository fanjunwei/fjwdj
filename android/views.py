# coding=utf-8
import json
from django import http
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.utils.decorators import classonlymethod
from django.views.generic import View
from django.views.decorators.cache import never_cache
from functools import update_wrapper
from android.auth2 import getAuth2Token

INVALID_LOGIN_PARAMETERS = 101
SESSION_TOKEN_ERROR_PARAMETERS = 102


def no_login_error(request, *args, **kwargs):
    data = {
        'code': INVALID_LOGIN_PARAMETERS,
        'error': '未登录',
    }
    return http.HttpResponseNotFound(json.dumps(data))


def login_view_decorator(func):
    def admin_view(cls, cached=False, **kwargs):
        view = func(cls, **kwargs)

        def has_login(request):
            if request.user.is_active:
                return True
            else:
                return False

        def inner(request, *args, **kwargs):
            if not has_login(request) and getattr(cls, 'need_login', True):
                return no_login_error(request, *args, **kwargs)
            return view(request, *args, **kwargs)

        if not cached:
            inner = never_cache(inner)
        return update_wrapper(inner, view)

    return admin_view


class JsonMixin(object):
    def get_context_data(self, **kwargs):
        return kwargs

    def render_to_response(self, context):
        return HttpResponse(json.dumps(context), 'application/json')


class JsonView(JsonMixin, View):
    need_login = True
    isPost = False
    override_response = None

    def get(self, request, *args, **kwargs):
        self.isPost = False
        context = self.get_context_data(**kwargs)
        if self.override_response:
            return self.override_response
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.isPost = True
        context = self.get_context_data(**kwargs)
        if self.override_response:
            return self.override_response
        return self.render_to_response(context)

    def response_error(self, code, error):
        data = {
            'code': code,
            'error': error,
        }
        self.override_response = http.HttpResponseNotFound(json.dumps(data))
        return None

    @classonlymethod
    @login_view_decorator
    def as_view(cls, **initkwargs):
        return super(JsonView, cls).as_view(**initkwargs)


class LoginView(JsonView):
    need_login = False

    def get_context_data(self, **kwargs):
        username = self.request.REQUEST.get('username')
        password = self.request.REQUEST.get('password')
        if username and password:
            user = authenticate(username=username,
                                password=password)
            if user is None:
                return self.response_error(INVALID_LOGIN_PARAMETERS, u'用户名或密码错误')
            elif not user.is_active:
                return self.response_error(INVALID_LOGIN_PARAMETERS, u'当前用户不可用')
            else:
                login(self.request, user)
                kwargs.update({
                    'username': user.username,
                    'nickname': user.first_name,
                    'authToken': getAuth2Token(user)
                })
        else:
            return self.response_error(INVALID_LOGIN_PARAMETERS, u'用户名和密码不能为空')
        return super(LoginView, self).get_context_data(**kwargs)


class UsersView(JsonView):
    def get_context_data(self, **kwargs):
        print(self.request.REQUEST)
        return super(UsersView, self).get_context_data(**kwargs)
