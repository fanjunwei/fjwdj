# coding=utf-8
# Date: 14/12/21
# Time: 22:58
# Email:fanjunwei003@163.com
import json
import uuid
from django.conf import settings
from django.http import HttpResponseNotFound
from android.auth2 import checkAuth2Token
from android.views import SESSION_TOKEN_ERROR_PARAMETERS

__author__ = u'范俊伟'


class AndroidAuthMiddleware(object):
    def process_request(self, request):
        auth2_token_key = request.META.get("HTTP_X_AUTH_TOKEN", None)
        if auth2_token_key:
            user = checkAuth2Token(auth2_token_key)
            if user:
                request.user = user
            elif user == None:
                data = {
                    'code': SESSION_TOKEN_ERROR_PARAMETERS,
                    'error': 'token错误',
                }
                return HttpResponseNotFound(json.dumps(data))

