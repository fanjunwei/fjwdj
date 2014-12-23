# coding=utf-8
# Date: 14/12/21
# Time: 22:58
# Email:fanjunwei003@163.com
import uuid
from django.conf import settings

__author__ = u'范俊伟'


class AndroidAuthMiddleware(object):
    def process_request(self, request):
        rest_session_key = request.META.get("HTTP_X_PARSE_SESSION_KEY", None)
        if rest_session_key:
            request.hasRestSessionToken = True
            request.COOKIES[settings.SESSION_COOKIE_NAME] = rest_session_key
        else:
            request.hasRestSessionToken = False
